import os
import click
import yaml

"""
Main function of the style,
should take the page body and return HTML
"""
def render_html(serif, config, body, css):

  data = yaml.load(body)

  print(data)

  # Run template
  click.echo("Rendering template")
  template = serif['jinja'].get_template("vit-invoice/template.html")
  html = template.render(data=data, css=css, config=config)

  return html