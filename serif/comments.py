from markdown.inlinepatterns import Pattern
from markdown.util import etree
import re
import sys

MARKER_PATTERN = r'==(.*?)=='

class MarkerPattern(Pattern):

  def handleMatch(self, m):
    el = etree.Element("mark")
    el.set('class','serif-marked')

    el.text = m.group(2)
    return el

marker_pattern = MarkerPattern(MARKER_PATTERN)

COMMENT_PATTERN = r'\(\(([\w ]+?): ?(.*?)\)\)'

class CommentPattern(Pattern):

  def handleMatch(self, m):
    el = etree.Element("span")
    el.set('class','serif-comment')

    author = etree.Element("span")
    author.set('class', 'serif-comment-author')
    author.text = m.group(2)
    el.append(author)

    message = etree.Element("span")
    message.set('class', 'serif-comment-message')
    message.text = m.group(3)
    el.append(message)

    return el

comment_pattern = CommentPattern(COMMENT_PATTERN)