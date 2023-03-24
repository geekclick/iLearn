from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename
import json
import os 
import math

with open('config.json', 'r') as s:
  params = json.load(s)["params"]

app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///ilearn.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = params['upload_location']
db = SQLAlchemy(app)

class Posts(db.Model):
  sno = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(80), nullable=False)
  desc = db.Column(db.String(100), nullable=False)
  content = db.Column(db.String(500), nullable=False)
  by = db.Column(db.String(50), nullable=False)
  slug = db.Column(db.String(25), nullable=False)
  img_file = db.Column(db.String(12), nullable=True)
  date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
  
  def __repr__(self) -> str:
    return f"{self.sno} - {self.title}"

class Contacts(db.Model):
  sno = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(80), nullable=False)
  email = db.Column(db.String(50), nullable=False)
  phone_num = db.Column(db.String(12), nullable=False)
  mes = db.Column(db.String(500), nullable=False)
  date = db.Column(db.Date, nullable=False, default=datetime.utcnow)

  def __repr__(self) -> str:
    return f"{self.sno} - {self.name}"


@app.route("/")
def home():
  posts = Posts.query.filter_by().all()
  last = math.ceil(len(posts)/int(params['num_of_posts']))
  page = request.args.get('page')
  if (not str(page).isnumeric()):
    page = 1
  page = int(page)
  posts = posts[(page-1)*int(params['num_of_posts']):(page-1)*int(params['num_of_posts'])+ int(params['num_of_posts'])]
  if page==1:
    prev = "#"
    nex = "/?page="+ str(page+1)
  elif page==last:
    prev = "/?page="+ str(page-1)
    nex = "#"
  else:
    prev = "/?page="+ str(page-1)
    nex = "/?page="+ str(page+1)

  return render_template('index.html', params=params, posts=posts, prev=prev, nex=nex)

@app.route("/about")
def about():
  return render_template('about.html', params=params)

@app.route("/contact", methods = ['GET', 'POST'])
def contact():
  if request.method == 'POST':
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    message = request.form.get('message')
    entry = Contacts(name=name, email=email, phone_num=phone, mes=message)
    db.session.add(entry)
    db.session.commit()

  return render_template('contact.html', params=params)

# @app.route("/post")
# def posts():
  # return render_template('post.html', params=params)

@app.route("/post/<string:post_slug>", methods = ['GET'])
def post_route(post_slug):
  post = Posts.query.filter_by(slug=post_slug).first()

  return render_template('post.html', params=params, post=post)

@app.route("/dashboard", methods = ['GET', 'POST'])
def dashboard():

  if ('user' in session and session['user']== params['admin_user']):
    posts = Posts.query.all()
    return render_template('dashboard.html', params=params, posts=posts)

  if request.method=='POST':
    username = request.form.get('uname')
    userpass = request.form.get('pass')
    if (username== params['admin_user'] and userpass== params['admin_password']):
      # set the session variable
      session['user'] = username
      posts = Posts.query.all()
      return render_template('dashboard.html', params=params, posts=posts)


  else:
    return render_template('login.html', params=params)

@app.route("/edit/<string:sno>", methods = ['GET', 'POST'])
def edit(sno):
  if ('user' in session and session['user']== params['admin_user']):
    if request.method == 'POST':
      box_title = request.form.get('title')
      subtitle = request.form.get('subtitle')
      content = request.form.get('content')
      slug = request.form.get('slug')
      img_file = request.form.get('img_file')

      if sno == '0':
        post = Posts(title=box_title, desc=subtitle, content=content, by=params['posted_by'], slug=slug, img_file=img_file)
        db.session.add(post)
        db.session.commit()

      else:
        post = Posts.query.filter_by(sno=sno).first()
        post.title = box_title
        post.desc = subtitle
        post.content = content
        post.slug = slug
        post.img_file = img_file
        db.session.commit()
        return redirect('/edit/'+sno)

    post = Posts.query.filter_by(sno=sno).first()
    return render_template('edit.html', params=params, post=post, sno=sno)

@app.route("/uploader", methods = ['GET', 'POST'])
def uploader():
  if ('user' in session and session['user']== params['admin_user']):
    if (request.method == 'POST'):
      f= request.files['file1']
      f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
      return "Uploaded Successfully"
  return render_template('about.html', params=params)    

@app.route("/logout")
def logout():
  session.pop('user')
  return redirect('/dashboard')

@app.route("/delete/<string:sno>", methods = ['GET', 'POST'])
def delete(sno):
  if ('user' in session and session['user']== params['admin_user']):
    post = Posts.query.filter_by(sno=sno).first()
    db.session.delete(post)
    db.session.commit()

  return redirect('/dashboard')



if __name__ == "__main__":
  app.run(debug=True)