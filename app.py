import ConfigParser
from flask import Flask, render_template, abort
app = Flask(__name__)

pages = []
sub_pages = {}

@app.route('/')
def index():
  recent = []
  for (page, links) in sub_pages.items():
    if links:
      recent.append((page, links[0]))
  return render_template('index.html', pages=pages, links=recent, current='index')

@app.route('/<page>/')
def go_to(page):
  page = linkname(page)
  if page in pages:
    print sub_pages[page]
    return render_template('pages/%s.html' % page, pages=pages, links=sub_pages[page], current=page)
  else:
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
  title = ''.join(c for c in title if c.isalnum() or c.isspace())
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

def init():
  cfg = ConfigParser.ConfigParser()
  cfg.read('pages.cfg')
  
  for (_, page) in cfg.items('pages'):
    pages.append(page)
    
    links = []
    for (_, link) in cfg.items(page):
      links.insert(0, link)
    sub_pages[page] = links

if __name__ == '__main__':
  init()
  app.run(host='0.0.0.0', debug=True)
  
