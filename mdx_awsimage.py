import re
import markdown
from markdown.util import etree

AWSIMAGE_RE = r'!(\[(.*?)\])?\{(.*?)\}'

class AWSImageExtension(markdown.Extension):
  def __init__(self, configs):
    self.config = { 'PREFIX': '' }
    
    for key, value in configs:
      self.config[key] = value

  def extendMarkdown(self, md, md_globals):
    md.registerExtension(self)
    md.inlinePatterns.add('awsimage', AWSImagePattern(AWSIMAGE_RE, self.config), '<reference')

class AWSImagePattern(markdown.inlinepatterns.Pattern):
  def __init__(self, pattern, config):
    markdown.inlinepatterns.Pattern.__init__(self, pattern)
    self.config = config

  def handleMatch(self, m):
    img = etree.Element('img')
    img.set('alt', m.group(3))
    img.set('src', self.config['PREFIX'] + m.group(4))
    return img

def makeExtension(configs=None):
  return AWSImageExtension(configs=configs)
