from markdown.inlinepatterns import Pattern
from markdown.util import etree
import raw_html
import svgmath
from markdown.util import AtomicString
from util import get
import click

MATH_PATTERN = r'(\${1,2})([^\$].*?)\${1,2}'

class MathPattern(Pattern):

  def __init__(self, serif_config):
    self.serif_config = serif_config
    super(MathPattern, self).__init__(MATH_PATTERN)

  def handleMatch(self, m):
    c = self.serif_config

    el = etree.Element("span")
    if len(m.group(2)) == 2:
      mode = svgmath.DISPLAY
      el.set('class', 'eqn-display')
    elif len(m.group(2)) == 1:
      mode = svgmath.INLINE
      el.set('class', 'eqn-inline')
    else:
      raise ValueError('Expecting either 1 or 2 $\'s.')
    formula = m.group(3).strip()
    try:
      click.echo("Rendering formula '%s'" % formula)
      rendered = svgmath.render(formula, mode=mode, font_family=get(c, 'math', 'font-family'))
    except:
      raise ValueError("Couldn't render formula '%s'" % formula)

    el.text = AtomicString(raw_html.encode(rendered['svg']))
    return el
