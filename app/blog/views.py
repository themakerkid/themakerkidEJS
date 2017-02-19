from datetime import datetime
from flask import render_template, flash, redirect, request, url_for, abort
from flask_login import login_user, logout_user, current_user, login_required
from forms import LoginForm, PostForm
from wtforms import ValidationError
from ..models import User, Post, db
from . import blog

@blog.route('/', methods=['GET', 'POST'])
def index():
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, body=form.body.data, author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('blog.post', id=post.id))
    return render_template("blog/index.html", title="Blog - Home Page", year=datetime.now().year, form=form, posts=posts)

@blog.route('/post/<int:id>')
@login_required
def post(id):
    post = Post.query.filter_by(id=id).first()
    if not post:
        abort(404)
    return render_template("blog/post.html", title="Post - " + post.title, year=datetime.now().year, post=post)

@blog.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    post = Post.query.filter_by(id=id).first()
    form = PostForm()
    if not post:
        abort(404)
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        return redirect(url_for('.post', id=id))
    form.title.data = post.title
    form.body.data = post.body
    return render_template("blog/edit.html", title="Edit Post - " + post.title, year=datetime.now().year, post=post, form=form)

@blog.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = form.validate_credentials(form.user_or_email, form.password)
        if user:
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('.index'))
        else:
            flash("You entered the wrong things!")
    return render_template("blog/login.html", form=form, title="Blog - Login", year=datetime.now().year)

@blog.route('/logout')
@login_required
def logout():
    name = current_user.username
    logout_user()
    flash("You have been logged out of the application, " + name + ".")
    return redirect(url_for('.index'))