import ConfigParser
from flask import Flask, render_template, abort
from flaskext.markdown import Markdown
app = Flask(__name__)
Markdown(app)

pages = []
sub_pages = {}

@app.route('/')
def index():
  recent = []
  for (page, titles) in sub_pages.items():
    if titles:
      recent.append((page, titles[0][1]))
  return render_template('index.html', pages=pages, titles=recent, current='index')

@app.route('/<page>/')
def go_to(page):
  page = linkname(page)
  if page in pages:
    print sub_pages[page]
    return render_template('pages/%s.html' % page, pages=pages, titles=get_titles(page), current=page)
  else:
    abort(404)

@app.route('/<page>/<link>/')
def item(page, link):
  page = linkname(page)
  link = linkname(link)
  print '/%s/%s/' % (page, link)
  print page in pages
  print is_link(page, link)
  if page in pages and is_link(page, link):
    try:
      f = open('markdown/%s/%s.md' % (page, link), 'rb')
      content = f.read()
      f.close()
    except:
      content = ''
    return render_template('/markdown.html', pages=pages, current=page, title=get_title(page, link), content=content)
  abort(404)

@app.errorhandler(404)
def page_not_found(e):
  return render_template('errors/404.html', pages=pages), 404

@app.errorhandler(500)
def internal_server_error(e):
  return render_template('errors/500.html', pages=pages), 500

# converts Title into link version
# example: "O' Green World" would become "o-green-world"
def linkname(title):
  title = ''.join(c for c in title if c.isalnum() or c.isspace() or c == '-')
  return title.lower().replace(' ', '-')

def link(title, page):
  return '/%s/%s/' % (page, linkname(title))

def thumbnail_on(title, page):
  return '/static/%s/%s/thumbnail-on.jpg' % (page, linkname(title)) 

def thumbnail_off(title, page):
  return '/static/%s/%s/thumbnail-off.jpg' % (page, linkname(title)) 

def icon_on(service):
  return '/static/images/%s-on.png' % linkname(service)

def icon_off(service):
  return '/static/images/%s-off.png' % linkname(service)

# add custom filters to jinja2
app.jinja_env.filters['linkname']      = linkname
app.jinja_env.filters['link']          = link
app.jinja_env.filters['thumbnail_on']  = thumbnail_on
app.jinja_env.filters['thumbnail_off'] = thumbnail_off
app.jinja_env.filters['icon_on']       = icon_on
app.jinja_env.filters['icon_off']      = icon_off

def get_titles(page):
  return [title for (_, title) in sub_pages[page]]

def get_links(page):
  return [link for (link, _) in sub_pages[page]]

def get_title(page, link):
  for (l, t) in sub_pages[page]:
    if link == l:
      return t

def is_title(page, title):
  for (_, t) in sub_pages[page]:
    if title == t:
      return True
  return False

def is_link(page, link):
  for (l, _) in sub_pages[page]:
    if link == l:
      return True
  return False

def init():
  cfg = ConfigParser.ConfigParser()
  cfg.read('pages.cfg')
  
  for (_, page) in cfg.items('pages'):
    pages.append(page)
    
    titles = []
    for (_, title) in cfg.items(page):
      titles.insert(0, (linkname(title), title))
    sub_pages[page] = titles

if __name__ == '__main__':
  init()
  app.run(host='0.0.0.0', debug=True)
  
