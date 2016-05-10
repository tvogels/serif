from markdown.blockprocessors import BlockProcessor
from markdown.util import etree
import re
import sys

class IncludesProcessor(BlockProcessor):

  def test(self, parent, block):
    return re.match(r"^\\include\((.*)\)$", block)

  def run(self, parent, blocks):
    path = re.match(r"^\\include\((.*)\)$", blocks[0]).group(1)
    del blocks[0]
    el = etree.Element("div")
    el.set('class', 'serif-include')
    with open(path, 'r') as f:
      el.text = self.parser.parseChunk(parent, f.read())
    parent.append(el)
