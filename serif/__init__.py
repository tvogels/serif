from markdown_extension import makeExtension
import markdown
import re

markdown.util.BLOCK_LEVEL_ELEMENTS = re.compile(
    "^(p|div|h[1-6]|blockquote|pre|table|dl|ol|ul"
    "|script|noscript|form|fieldset|iframe|math"
    "|hr|hr/|style|li|dt|dd|thead|tbody"
    "|tr|th|td|section|footer|header|group|figure"
    "|figcaption|aside|article|canvas|output"
    "|lemma|proof|theorem|caption|listing"
    "|progress|video|nav)$",
    re.IGNORECASE
)

# interesting extension: critic

markdown = markdown.Markdown(extensions=[
  'extra',
  'smarty',
  'codehilite',
  'headerid',
  'toc',
  'serif',
  'outline',
], extension_configs = {
  "toc": {
    "marker": "\\toc()",
    "title": "Table of Contents"
  }
})