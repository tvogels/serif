import markdown
from markdown.inlinepatterns import Pattern
from markdown.util import etree
import raw_html
import math
import sys
from util import get
import citations
from placeholders import BibliographyProcessor, ListOfFiguresProcessor, PageBreakProcessor
from includes import IncludesProcessor
from no_wrap import no_wrap
from comments import marker_pattern, comment_pattern


from markdown.treeprocessors import Treeprocessor


class SerifExtension(markdown.extensions.Extension):

  def __init__(self, serif_config, cache, **kwargs):
    self.config = {}
    self.serif_config = serif_config
    self.cache = cache
    super(SerifExtension, self).__init__(**kwargs)

  def extendMarkdown(self, md, md_globals):
    md.registerExtension(self)

    c = self.serif_config

    md.inlinePatterns.add('no_wrap', no_wrap, "<strong")

    if get(c, 'math', 'enabled'):
      md.inlinePatterns.add('math', math.MathPattern(c, self.cache('svgmath')), "<backtick")
      md.postprocessors.add('raw', raw_html.RawPostprocessor(), "_end")


    if get(c, 'comments', 'enabled'):
      md.inlinePatterns.add('markings', marker_pattern, "_end")
      md.inlinePatterns.add('comments', comment_pattern, ">markings")


    if get(c, 'bibliography', 'enabled'):
      md.inlinePatterns.add('citation_blocks', citations.block_pattern, "_begin")
      md.inlinePatterns.add('references', citations.reference_pattern, ">citation_blocks")
      md.parser.blockprocessors.add('bibliography_placeholder', BibliographyProcessor(md.parser), "_begin")

    md.parser.blockprocessors.add('figure_list_placeholder', ListOfFiguresProcessor(md.parser), "_begin")
    md.parser.blockprocessors.add('page_break_placeholder', PageBreakProcessor(md.parser), "_begin")
    md.parser.blockprocessors.add('includes', IncludesProcessor(md.parser), "_begin")


def makeExtension(**kwargs):
  return SerifExtension({}, **kwargs)