from jinja2 import Environment, PackageLoader
jinja_env = Environment(loader=PackageLoader('serif'))

"""
Main function of the style, 
should take the page body and return HTML
"""

def render_html(serif, config, body, css):

	# Run Markdown
	html_body = serif.markdown(body, config)

	# Run template
	template = jinja_env.get_template("serif-plain/template.jinja2")
	html = template.render(body=body, css=css, config=config)

	# Run linking (bibliography, counters, etc.)
	html = serif.link(html)

	return html