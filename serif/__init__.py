from markdown_extension import SerifExtension
import markdown
import re
import click
import yaml
import sys, os
from util import merge_dictionaries, get
import jinja2
import execjs
import json
from copy import copy

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


def get_markdown(config):
  """
  Get a configured instance of the Markdown parser
  """
  extensions = copy(config['markdown']['extensions'])
  extconfigs = copy(config['markdown']['extension_configs'])
  extensions.append(SerifExtension(config))
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
  js_script = js_script.replace('[[CONFIG_PLACEHOLDER]]', json.dumps(config))

  # Inject path
  path_script = """
  module.paths.push('%s');
  """ % os.path.join(os.path.dirname(__file__),'node_modules')
  js_script = path_script + js_script

  context = execjs.compile(js_script)
  return lambda html: context.call('link', html)
  


@click.command()
@click.argument('input_file', type=click.File('r'))
@click.option('--keep-html/--no-keep-html', default=False)
def cli(input_file, keep_html):
  # Read configuration block
  config, body = read_config(input_file.read())

  # Check if a theme is provided
  if 'theme' not in config:
    terminate("Please specify a theme in the YAML configuration on top of the file.")

  # Load the theme
  theme = __import__(config['theme'])
  
  # Merge configurations at global, theme and document levels
  config = resolve_config(config, theme.config)

  # Create toolset for the theme to work with
  toolset = {
    'markdown': get_markdown(config).convert if 'markdown' in config and config['markdown'] else None,
    'jinja': get_jinja(config),
    'link': get_linker(config)
  }

  # print(body)
  print(toolset['link'](toolset['markdown'](body)))
  # print(toolset['link'](toolset['markdown'](body)))
