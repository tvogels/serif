from markdown.inlinepatterns import Pattern
from markdown.util import etree
import raw_html
import svgmath
from markdown.util import AtomicString

MATH_PATTERN = r'(\${1,2})([^\$].*?)\${1,2}'

class MathPattern(Pattern):
  def handleMatch(self, m):
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
      rendered = svgmath.render(formula,mode=mode, font_family="Times")
    except:
      raise ValueError("Couldn't render formula '%s'" % formula)

    el.text = AtomicString(raw_html.encode(rendered['svg']))
    return el

pattern = MathPattern(MATH_PATTERN)