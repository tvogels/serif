import re
import json
from markdown.inlinepatterns import Pattern
from markdown.util import etree
import sys
from markdown.util import AtomicString

BLOCK_CITATION = r'\[([\w ]*.?@.+?)?\]'
class CitationPattern(Pattern):
  def parseEntry(self, string):
    m = re.match(r'([\w ]*)([-]?)@(bib:)?([\w\-]+)(, (.*?))?(,(.*?))?$', string)
    if not m:
      raise ValueError("Citation '%s' could not be interpreted." % string)
    else:
      return {
        'id': m.group(4),
        'prefix': m.group(1),
        'suppress-author': m.group(2) == '-',
        'locator': m.group(6),
        'suffix': m.group(8)
      }
    return string

  def handleMatch(self, m):
    el = etree.Element('a')
    entries = [self.parseEntry(e.strip()) for e in m.group(2).split(";")]
    el.text = AtomicString(m.group(2))
    el.set('class','serif-citation-block')
    el.set('data-items', json.dumps(entries))
    return el

block_pattern = CitationPattern(BLOCK_CITATION)



SIMPLE_REFERENCE = r'(^|(?<=\s))@((\w+):)?([\w-]+)'
class ReferencePattern(Pattern):

  def handleMatch(self, m):
    el = etree.Element('a')
    prefix = m.group(3) if m.group(3) else ""
    el.set('href','#%s%s' % (prefix, m.group(5)))
    el.set('class', 'serif-reference')
    el.set('data-reference-type', m.group(3)[:-1] if m.group(3) else 'bib')
    # el.text = m.group(5)
    return el

reference_pattern = ReferencePattern(SIMPLE_REFERENCE)


