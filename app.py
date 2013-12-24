import os
import boto
from datetime import datetime
from functools import wraps
from markdown import markdown as md
from mimetypes import guess_type
from flask import *
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, login_required, current_user, login_user, logout_user
from flask.ext.bcrypt import Bcrypt
from werkzeug.utils import secure_filename

# S3 connection
s3_conn = boto.connect_s3()
s3_bucket = s3_conn.get_bucket('vineel.me')
s3_key = boto.s3.key.Key(s3_bucket)

# Database connection
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://vineelme:vineelme@localhost/vineelme')
db = SQLAlchemy(app)

# Bcrypt
bcrypt = Bcrypt(app)

# Database object models

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(80), unique=True)
  password = db.Column(db.String(120))

  def __init__(self, username, password):
    self.username = username
    self.password = password

  def __repr__(self):
    return '<User %s>' % self.username

  # Needed for flask-login

  def is_authenticated(self):
    return True

  def is_active(self):
    return True

  def is_anonymous(self):
    return False

  def get_id(self):
    return unicode(self.username)

class Post(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(80), unique=True)
  link = db.Column(db.String(80), unique=True)
  body = db.Column(db.Text)
  pub_date = db.Column(db.DateTime)
  published = db.Column(db.Boolean)

  category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
  category = db.relationship('Category', backref=db.backref('posts', lazy='dynamic'))

  def __init__(self, title, body, category, pub_date=None, published=False):
    self.title = title
    self.link = linkname(title)
    self.body = body
    if pub_date is None:
      pub_date = datetime.utcnow()
    self.pub_date = pub_date
    self.published = published
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

# Public views

@app.route('/')
def index():
  posts = Post.query.filter_by(published=True).order_by(Post.pub_date.desc()).limit(6).all()
  pages = [ c.name for c in Category.query.order_by(Category.index).all() ]
  return render_template('index.html', pages=pages, posts=posts, current='index', admin=current_user.is_authenticated())

@app.route('/<page>/')
def go_to(page):
  page = linkname(page)
  category = Category.query.filter_by(name=page).first_or_404()
  pages = [ c.name for c in Category.query.order_by(Category.index).all() ]
  posts = category.posts.filter_by(published=True).order_by(Post.pub_date.desc()).all()

  return render_template('pages/%s.html' % page, pages=pages, posts=posts, current=page, admin=current_user.is_authenticated())

@app.route('/<page>/<title>/')
def item(page, title):
  post = Post.query.filter_by(link=linkname(title)).first_or_404()
  if not current_user.is_authenticated() and not post.published:
    abort(404)
  if not post.category.name == linkname(page):
    return redirect(link(post))
  pages = [ c.name for c in Category.query.order_by(Category.index) ]
  return render_template('/markdown.html', pages=pages, current=page, post=post, admin=current_user.is_authenticated())

# Admin views

def ssl_required(fn):
  @wraps(fn)
  def decorated_view(*args, **kwargs):
    # Redirect to piggyback herokuapp.com SSL
    if 'vineel.me' in request.url:
      return redirect(request.url.replace(request.url_root, 'https://vineel.herokuapp.com/'))
    return fn(*args, **kwargs)

  return decorated_view

@app.route('/admin/')
def admin():
  if current_user.is_authenticated():
    return redirect(url_for('admin_posts'))
  else:
    return redirect(url_for('admin_login'))

@app.route('/admin/login/', methods=['POST', 'GET'])
@ssl_required
def admin_login():
  if request.method == 'POST':
    user = User.query.filter_by(username=request.form['username']).first()
    if user and bcrypt.check_password_hash(user.password, request.form['password']):
      login_user(user)
      return redirect(request.args.get('next') or url_for('admin_posts'))
  if current_user.is_authenticated():
    return redirect(url_for('admin_posts'))
  pages = [ c.name for c in Category.query.order_by(Category.index) ]
  return render_template('admin/login.html', pages=pages)

@app.route('/admin/logout/')
@login_required
@ssl_required
def admin_logout():
  logout_user()
  return redirect(request.referrer)

@app.route('/admin/posts/')
@login_required
@ssl_required
def admin_posts():
  pages = [ c.name for c in Category.query.order_by(Category.index) ]
  posts = Post.query.filter_by(published=True).order_by(Post.pub_date.desc()).all()
  drafts = Post.query.filter_by(published=False).order_by(Post.pub_date.desc()).all()
  return render_template('admin/posts.html', pages=pages, posts=posts, drafts=drafts, admin=current_user.is_authenticated())

@app.route('/admin/publish/<id>/', methods=['POST'])
@login_required
@ssl_required
def admin_publish(id):
  if not id.isdigit():
    abort(404)
  post = Post.query.filter_by(id=int(id)).first_or_404()
  
  post.published = True
  db.session.commit()

  return redirect(request.referrer or url_for('admin_posts'))

@app.route('/admin/unpublish/<id>/', methods=['POST'])
@login_required
@ssl_required
def admin_unpublish(id):
  if not id.isdigit():
    abort(404)
  post = Post.query.filter_by(id=int(id)).first_or_404()

  post.published = False
  db.session.commit()

  return redirect(request.referrer or url_for('admin_posts'))

@app.route('/admin/edit/<id>/', methods=['POST', 'GET'])
@login_required
@ssl_required
def admin_edit(id):
  if not id.isdigit():
    abort(404)
  post = Post.query.filter_by(id=int(id)).first_or_404()

  if request.method == 'POST':
    post.category = Category.query.filter_by(name=request.form['category']).first_or_404()
    post.title = request.form['title']
    post.link = linkname(post.title)
    post.body = request.form['text']
    db.session.commit()
    return redirect(link(post))

  pages = [ c.name for c in Category.query.order_by(Category.index) ]
  images = [ i.name[len(str(post.id)) + 1:] for i in s3_bucket.list(prefix='%s/' % post.id) if i.name != '%s/' % post.id]
  return render_template('admin/edit.html', pages=pages, post=post, images=images, admin=current_user.is_authenticated())

@app.route('/admin/new/', methods=['POST', 'GET'])
@login_required
@ssl_required
def admin_new():
  if request.method == 'POST':
    category = Category.query.filter_by(name=request.form['category']).first_or_404()
    post = Post(request.form['title'], request.form['text'], category)
    db.session.add(post)
    db.session.commit()
    return redirect(link(post))
  pages = [ c.name for c in Category.query.order_by(Category.index) ]
  return render_template('admin/new.html', pages=pages, admin=current_user.is_authenticated())

@app.route('/admin/delete/<id>/', methods=['POST'])
@login_required
@ssl_required
def admin_delete(id):
  if not id.isdigit():
    abort(404)
  post = Post.query.filter_by(id=int(id)).first_or_404()

  for item in s3_bucket.list('%s/' % post.id):
    s3_key.key = item.name
    s3_key.delete()

  db.session.delete(post)
  db.session.commit()

  return redirect(request.referrer or url_for('admin_posts'))

@app.route('/admin/image/new/<id>/', methods=['POST'])
@login_required
@ssl_required
def admin_image_new(id):
  if not id.isdigit():
    abort(404)
  post = Post.query.filter_by(id=int(id)).first_or_404()

  file = request.files['image']
  filename = secure_filename(file.filename)
  s3_key.key = '%s/%s' % (post.id, filename)
  s3_key.set_metadata('Content-Type', guess_type(filename)[0])
  s3_key.set_contents_from_file(file)
  s3_key.set_acl('public-read')

  return redirect(request.referrer or edit(post))

@app.route('/admin/image/delete/<id>/<image>/', methods=['POST'])
@login_required
@ssl_required
def admin_image_delete(id, image):
  if not id.isdigit():
    abort(404)
  post = Post.query.filter_by(id=int(id)).first_or_404()
  
  s3_key.key = '%s/%s' % (id, image)
  s3_key.delete()

  return redirect(request.referrer or edit(post))

# Login management
login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = os.environ.get('APP_SECRET_KEY', 'haha, nice try!')
login_manager.login_view = 'admin_login'

@login_manager.user_loader
def load_user(username):
  return User.query.filter_by(username=username).first()

# Error views

@app.errorhandler(404)
def page_not_found(e):
  pages = [ c.name for c in Category.query.order_by(Category.index).all() ]
  return render_template('errors/404.html', pages=pages, admin=current_user.is_authenticated()), 404

@app.errorhandler(500)
def internal_server_error(e):
  pages = [ c.name for c in Category.query.order_by(Category.index).all() ]
  return render_template('errors/500.html', pages=pages, admin=current_user.is_authenticated()), 500

def jinja_filter(fn):
  app.jinja_env.filters[fn.__name__] = fn
  return fn

# converts Title into link version
# example: "O' Green World" would become "o-green-world"
@jinja_filter
def linkname(title):
  title = title.strip()
  title = ''.join(c for c in title if c.isalnum() or c.isspace() or c == '-')
  return title.lower().replace(' ', '-')

@jinja_filter
def link(post):
  return '/%s/%s/' % (post.category.name, post.link)

@jinja_filter
def thumbnail_on(post):
  return 'https://s3.amazonaws.com/vineel.me/%s/thumbnail-on.jpg' % post.id 

@jinja_filter
def thumbnail_off(post):
  return 'https://s3.amazonaws.com/vineel.me/%s/thumbnail-off.jpg' % post.id 

@jinja_filter
def icon_on(service):
  return '/static/images/%s-on.png' % linkname(service)

@jinja_filter
def icon_off(service):
  return '/static/images/%s-off.png' % linkname(service)

@jinja_filter
def markdown(post):
  page = linkname(post.category.name)
  prefix = 'https://s3.amazonaws.com/vineel.me/%s/' % post.id
  return Markup(md(post.body, ['awsimage(PREFIX=%s)' % prefix, 'syntax']))

@jinja_filter
def edit(post):
  return '/admin/edit/%s/' % post.id

@jinja_filter
def publish(post):
  return '/admin/publish/%s/' % post.id

@jinja_filter
def unpublish(post):
  return '/admin/unpublish/%s/' % post.id

@jinja_filter
def delete(post):
  return '/admin/delete/%s/' % post.id

@jinja_filter
def image_url(image, post):
  return 'https://s3.amazonaws.com/vineel.me/%s/%s' % (post.id, image)

@jinja_filter
def image_delete(image, post):
  return '/admin/image/delete/%s/%s/' % (post.id, image)

if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port, debug=True)
  
