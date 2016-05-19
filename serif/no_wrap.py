from markdown.inlinepatterns import Pattern
from markdown.util import etree


PATTERNS = []

# Math patterns
MATH_AFTER   = r"""[,\.\-;!\?\)\]]"""
MATH_BEFORE  = r"""[\(\[]"""
PATTERNS.append(r"""(%s\$[^\$]+\$%s*)""" % (MATH_BEFORE, MATH_AFTER))
PATTERNS.append(r"""(%s?\$[^\$]+\$%s+)""" % (MATH_BEFORE, MATH_AFTER))

# Last words of paragraph
PATTERNS.append(r"""(\w+ \w+[\.\?!]\s*$)""")


NO_WRAP_PATTERN = "(%s)" % ("|".join(PATTERNS))

class NoWrap(Pattern):
  def handleMatch(self, m):
    el = etree.Element("span")
    el.set('class', 'no-break')
    el.text = m.group(2)
    return el


no_wrap = NoWrap(NO_WRAP_PATTERN)

