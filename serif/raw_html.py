import base64
from markdown.postprocessors import Postprocessor
import re

def encode(string):
  return "!!RAW:%s:ENDRAW!!" % base64.b64encode(string)

DECODE = re.compile(r'\!\!RAW\:(.*?)\:ENDRAW\!\!')

class RawPostprocessor(Postprocessor):
  def run(self, text):
    return DECODE.sub(
      lambda m: base64.b64decode(m.group(1)),
      text
    )
