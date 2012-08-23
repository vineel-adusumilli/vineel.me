import re
import markdown
from markdown.util import etree
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

SYNTAX_RE = r'```(\S*)\s(.*?)```'

class SyntaxExtension(markdown.Extension):
  def extendMarkdown(self, md, md_globals):
    md.registerExtension(self)
    md.inlinePatterns.add('syntax', SyntaxPattern(SYNTAX_RE), '_begin')

class SyntaxPattern(markdown.inlinepatterns.Pattern):
  def handleMatch(self, m):
    language = m.group(2) or 'text'
    code = m.group(3)
    try:
      lexer = get_lexer_by_name(language)
    except:
      lexer = get_lexer_by_name('text')
    formatter = HtmlFormatter(cssclass='source', noclasses=True)
    source = etree.fromstring(highlight(code, lexer, formatter))
    return source

def makeExtension(configs=None):
  return SyntaxExtension()
