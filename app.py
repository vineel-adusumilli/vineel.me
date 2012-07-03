from flask import Flask, render_template
app = Flask(__name__)

pages = ['projects', 'experiments', 'articles', 'about', 'contact']

@app.route('/')
def index():
  return render_template('index.html', pages=pages, current='index')

@app.route('/<page>/')
def go_to(page):
  if page in pages:
    return render_template('%s.html' % page, title=page, pages=pages, current=page)
  else:
    abort(404)

if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)
  