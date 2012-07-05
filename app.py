from flask import Flask, render_template, abort
app = Flask(__name__)

pages = ['projects', 'experiments', 'articles', 'about', 'contact']

@app.route('/')
def index():
  return render_template('index.html', pages=pages, current='index')

@app.route('/<page>/')
def go_to(page):
  if page in pages:
    return render_template('pages/%s.html' % page, title=page, pages=pages, current=page)
  else:
    abort(404)

@app.errorhandler(404)
def page_not_found(e):
  return render_template('errors/404.html', title='404', pages=pages), 404

@app.errorhandler(500)
def internal_server_error(e):
  return render_template('errors/500.html', title='500', pages=pages), 500

if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=False)
  