import os
from jinja2 import Environment, FileSystemLoader

# Load Jinja2 environment for template rendering
SERIF_ROOT = os.path.join(os.path.dirname(__file__), "..")
jinja_env = Environment(loader=FileSystemLoader(SERIF_ROOT))


"""
Main function of the style, 
should take the page body and return HTML
"""
def render_html(serif, config, body, css):

	# Run Markdown
	html_body = serif.markdown(body)

	# Run template
	template = serif.jinja.get_template("serif-plain/template.html")
	html = template.render(body=body, css=css, config=config)

	# Run linking (bibliography, counters, etc.)
	html = serif.link(html, config)

	return html