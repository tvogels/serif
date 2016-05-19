from markdown_extension import SerifExtension
import markdown
import re
import click
import yaml
import sys, os
from util import merge_dictionaries, get, which
import jinja2
import execjs
import json
from copy import copy
import tempfile
import shutil
import io
import subprocess
from cache import SerifCache
DEVNULL = open(os.devnull, 'wb')

LINK_FILE_JS = os.path.join(os.path.dirname(__file__), "link.js")

markdown.util.BLOCK_LEVEL_ELEMENTS = re.compile(
    "^(p|div|h[1-6]|blockquote|pre|table|dl|ol|ul"
    "|script|noscript|form|fieldset|iframe|math"
    "|hr|hr/|style|li|dt|dd|thead|tbody"
    "|tr|th|td|section|footer|header|group|figure"
    "|figcaption|aside|article|canvas|output"
    "|lemma|proof|theorem|caption|listing"
    "|progress|video|nav)$",
    re.IGNORECASE
)


def terminate(message, e=None):
  """
  Terminate the CLI with a nicely formatted error
  """
  click.echo(click.style("!! %s" % message, fg='red'))
  if e:
    click.echo(e)
  sys.exit()


def read_config(markdown):
  """
  Read the configuration block at the top of a serif input file
  """
  regex = re.compile(r'-{3,}\n(.*?)\n-{3,}\n(.*)$',
                     re.MULTILINE|re.DOTALL)
  m = regex.match(markdown)

  if m:
    try:
      return yaml.load(m.group(1)), m.group(2)
    except yaml.scanner.ScannerError as e:
      terminate("Unable to parse YAML configuration on top of the file.", e)
  else:
    return {}, markdown


def resolve_config(document_config, theme_config, serif_config=None):
  # Make sure we have the Serif config loaded
  if not serif_config:
    f = os.path.join(os.path.dirname(__file__), "base_config.yml")
    serif_config = yaml.load(file(f, 'r'))

  merged = merge_dictionaries(
             merge_dictionaries(serif_config, theme_config),
             document_config
           )

  if 'locale' in merged and not 'language' in merged:
    merged['language'] = merged['locale'].split("_")[0]

  if 'author' in merged and not 'authors' in merged:
    merged['authors'] = [merged['author']]

  return merged


def get_markdown(config, cache):
  """
  Get a configured instance of the Markdown parser
  """
  extensions = copy(config['markdown']['extensions'])
  extconfigs = copy(config['markdown']['extension_configs'])
  extensions.append(SerifExtension(config, cache))
  try:
    return markdown.Markdown(
      extensions = extensions,
      extension_configs = extconfigs
    )
  except RuntimeError as e:
    terminate("Loading Markdown failed", e)


def get_jinja(config):
  """
  Get a configured instance of the Jinja2 template library.
  """
  SERIF_ROOT = os.path.join(os.path.dirname(__file__), "..")
  loader     = jinja2.FileSystemLoader(SERIF_ROOT)

  return jinja2.Environment(loader=loader)


def get_linker(config):
  with open(LINK_FILE_JS, 'r') as f:
    js_script = f.read()

  # Inject config
  js_script = js_script.replace(
    '[[CONFIG_PLACEHOLDER]]',
    json.dumps(config), 1
  )
  js_script = js_script.replace(
    '[[SERIF_ROOT]]',
    os.path.join(os.path.dirname(__file__), '..')
  )
  js_script = js_script.replace(
    '[[WORKING_DIRECTORY]]',
    os.getcwd(), 1
  )

  # Inject path
  path_script = """
  module.paths.push('%s');
  module.paths.push('%s');
  """ % (os.path.join(os.path.dirname(__file__),'node_modules'),
         os.path.join(os.path.dirname(__file__),'vendor'))
  js_script = path_script + js_script

  context = execjs.compile(js_script)
  return lambda html: context.call('link', html)



@click.command()
@click.argument('input_path', type=click.Path(exists=True))
@click.option('--keep-html/--no-keep-html', default=False)
def cli(input_path, keep_html):

  if not which('stylus'):
    terminate("I cannot find the stylus binary.")

  if not which('prince'):
    terminate("I cannot find the Prince binary.")

  file_base = os.path.splitext(os.path.abspath(input_path))[0]

  with io.open(input_path, 'r', encoding="utf-8") as input_file:

    # Read configuration block
    config, body = read_config(input_file.read())

    # Check if a theme is provided
    if 'theme' not in config:
      terminate("Please specify a theme in the YAML configuration on top of the file.")

    # Load the theme
    click.echo("Loading theme")
    theme = __import__(config['theme'])

    # Merge configurations at global, theme and document levels
    config = resolve_config(config, theme.config)

    # Create/load the cache
    cache = SerifCache('%s.serifcache' % file_base)

    # Create toolset for the theme to work with
    click.echo("Loading toolset")
    toolset = {
      'markdown': get_markdown(config, cache).convert if 'markdown' in config and config['markdown'] else None,
      'jinja': get_jinja(config),
      'link': get_linker(config)
    }

    # Make a temporary directory
    try:
      tmpdir = tempfile.mkdtemp()

      # Render the css
      click.echo("Rendering stylesheet")
      base_style  = os.path.join(os.path.dirname(__file__), 'base_styles.styl')
      theme_style = os.path.join(theme.directory, 'theme.styl')
      config_file = os.path.join(tmpdir, "config.js")
      with open(config_file, 'w') as cf:
        cf.write("""
        data = %s;
        module.exports = exports = function () {
          return function (style) {
            function define(data, prefix) {
              for (var key in data) {
                if (typeof data[key] === "object")
                  define(data[key], prefix + key + '_');
                else
                  style.define(prefix + key, data[key]);
              }
            }

            define(data, "config_");
          };
        };
        """ % json.dumps(config))
      subprocess.check_call(['stylus',
                             '--import', base_style,
                             theme_style,
                             '--out', tmpdir,
                             '--use', config_file], stdout=DEVNULL)

      with io.open(os.path.join(tmpdir, "theme.css"), 'r', encoding='utf-8') as cssfile:
        css = cssfile.read()

      click.echo("Running the theme")
      html = theme.render_html(toolset, config, body, css)

      html_location = '%s.html' % file_base

      # Save the cache
      cache.persist()

      # Write HTML to file
      try:
        with io.open(html_location, 'w', encoding='utf-8') as f:
          f.write(html)

        pdf_location = '%s.pdf' % file_base

        # Run Prince XML
        click.echo("Running Prince")
        subprocess.check_call(['prince',
                               html_location,
                               pdf_location
                              ], stdout=DEVNULL)
      finally:
        if not keep_html:
          os.remove(html_location)

    finally:
      shutil.rmtree(tmpdir)

