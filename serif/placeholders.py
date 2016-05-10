from markdown.blockprocessors import BlockProcessor
from markdown.util import etree
import sys

class BibliographyProcessor(BlockProcessor):

  def test(self, parent, block):
    return block == "\\bibliography()"

  def run(self, parent, blocks):
    del blocks[0]
    el = etree.Element("div")
    el.set('class', 'serif-bibliography')
    el.set('id', 'serif-bibliography')
    parent.append(el)


class ListOfFiguresProcessor(BlockProcessor):

  def test(self, parent, block):
    return block == "\\listoffigures()"

  def run(self, parent, blocks):
    del blocks[0]
    el = etree.Element("div")
    el.set('class', 'serif-list-of-figures')
    parent.append(el)


class PageBreakProcessor(BlockProcessor):

  def test(self, parent, block):
    return block == "\\pagebreak()"

  def run(self, parent, blocks):
    del blocks[0]
    el = etree.Element("div")
    el.set('class', 'serif-page-break')
    parent.append(el)
