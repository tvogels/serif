import os
import click

"""
Main function of the style,
should take the page body and return HTML
"""
def render_html(serif, config, body, css):

  # Run Markdown
  click.echo("Running markdown")
  html_body = serif['markdown'](body)

  # Run template
  click.echo("Rendering template")
  template = serif['jinja'].get_template("serif-plain/template.html")
  html = template.render(body=html_body, css=css, config=config)

  # Run linking (bibliography, counters, etc.)
  click.echo("Linking")
  html = serif['link'](html)

  return html