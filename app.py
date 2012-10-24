import os
from datetime import datetime
from markdown import markdown as md
from flask import Flask, Markup, render_template, abort
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://vineelme:vineelme@localhost/vineelme')
db = SQLAlchemy(app)

class Post(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(80), unique=True)
  link = db.Column(db.String(80), unique=True)
  body = db.Column(db.Text)
  pub_date = db.Column(db.DateTime)

  category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
  category = db.relationship('Category', backref=db.backref('posts', lazy='dynamic'))

  def __init__(self, title, body, category, pub_date=None):
    self.title = title
    self.link = linkname(title)
    self.body = body
    if pub_date is None:
      pub_date = datetime.utcnow()
    self.pub_date = pub_date
    self.category = category

  def __repr__(self):
    return '<Post %r>' % self.title

class Category(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(50), unique=True)
  index = db.Column(db.Integer, unique=True)

  def __init__(self, name, index):
    self.name = name
    self.index = index

  def __repr__(self):
    return '<Category %r>' % self.name

@app.route('/')
def index():
  recent = [ (p.category.name, p.title) for p in Post.query.order_by(Post.pub_date.desc()).limit(6).all() ]
  pages = [ c.name for c in Category.query.order_by(Category.index).all() ]
  return render_template('index.html', pages=pages, titles=recent, current='index')

@app.route('/<page>/')
def go_to(page):
  page = linkname(page)
  category = Category.query.filter_by(name=page).first_or_404()
  pages = [ c.name for c in Category.query.order_by(Category.index).all() ]
  titles = [ p.title for p in category.posts.order_by(Post.pub_date.desc()).all() ]

  return render_template('pages/%s.html' % page, pages=pages, titles=titles, current=page)

@app.route('/<page>/<link>/')
def item(page, link):
  page = linkname(page)
  link = linkname(link)
  pages = [ c.name for c in Category.query.order_by(Category.index) ]
  post = Post.query.filter_by(link=link).first_or_404()
  return render_template('/markdown.html', pages=pages, current=page, title=post.title, content=post.body)

@app.errorhandler(404)
def page_not_found(e):
  pages = [ c.name for c in Category.query.order_by(Category.index).all() ]
  return render_template('errors/404.html', pages=pages), 404

@app.errorhandler(500)
def internal_server_error(e):
  pages = [ c.name for c in Category.query.order_by(Category.index).all() ]
  return render_template('errors/500.html', pages=pages), 500

# converts Title into link version
# example: "O' Green World" would become "o-green-world"
def linkname(title):
  title = title.strip()
  title = ''.join(c for c in title if c.isalnum() or c.isspace() or c == '-')
  return title.lower().replace(' ', '-')

def link(title, page):
  return '/%s/%s/' % (page, linkname(title))

def thumbnail_on(title, page):
  return 'https://s3.amazonaws.com/vineel.me/%s/%s/thumbnail-on.jpg' % (page, linkname(title)) 

def thumbnail_off(title, page):
  return 'https://s3.amazonaws.com/vineel.me/%s/%s/thumbnail-off.jpg' % (page, linkname(title)) 

def icon_on(service):
  return '/static/images/%s-on.png' % linkname(service)

def icon_off(service):
  return '/static/images/%s-off.png' % linkname(service)

def markdown(text, title=None, page=None):
  prefix = ''
  if title and page:
    title = linkname(title)
    page = linkname(page)
    prefix = 'https://s3.amazonaws.com/vineel.me/%s/%s/' % (page, title)

  return Markup(md(text, ['awsimage(PREFIX=%s)' % prefix, 'syntax']))

# add custom filters to jinja2
app.jinja_env.filters['linkname']      = linkname
app.jinja_env.filters['link']          = link
app.jinja_env.filters['thumbnail_on']  = thumbnail_on
app.jinja_env.filters['thumbnail_off'] = thumbnail_off
app.jinja_env.filters['icon_on']       = icon_on
app.jinja_env.filters['icon_off']      = icon_off
app.jinja_env.filters['markdown']      = markdown

if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port, debug=False)
  
