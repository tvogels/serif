import markdown
from markdown.inlinepatterns import Pattern
from markdown.util import etree
import raw_html
import math_pattern
import sys
import citations
from placeholders import BibliographyProcessor, ListOfFiguresProcessor, PageBreakProcessor
from includes import IncludesProcessor
from comments import marker_pattern, comment_pattern


from markdown.treeprocessors import Treeprocessor


class SerifExtension(markdown.extensions.Extension):

  def __init__(self, **kwargs):
    self.config = {}
    super(SerifExtension, self).__init__(**kwargs)

  def extendMarkdown(self, md, md_globals):
    md.registerExtension(self)

    md.inlinePatterns.add('math', math_pattern.pattern, "<strong")
    md.inlinePatterns.add('citation_blocks', citations.block_pattern, "<math")
    md.inlinePatterns.add('references', citations.reference_pattern, ">citation_blocks")
    md.inlinePatterns.add('markings', marker_pattern, ">references")
    md.inlinePatterns.add('comments', comment_pattern, ">markings")

    md.postprocessors.add('raw', raw_html.RawPostprocessor(), "_end")

    md.parser.blockprocessors.add('bibliography_placeholder', BibliographyProcessor(md.parser), "_begin")
    md.parser.blockprocessors.add('figure_list_placeholder', ListOfFiguresProcessor(md.parser), "_begin")
    md.parser.blockprocessors.add('page_break_placeholder', PageBreakProcessor(md.parser), "_begin")
    md.parser.blockprocessors.add('includes', IncludesProcessor(md.parser), "_begin")


def makeExtension(**kwargs):
    return SerifExtension(**kwargs)