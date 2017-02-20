from datetime import datetime
from flask import render_template, flash, redirect, request, url_for, abort
from flask_login import login_user, logout_user, current_user, login_required
from forms import LoginForm, PostForm, CommentForm, RegisterForm, EditProfile
from wtforms import ValidationError
from ..models import Comment, User, Post, db
from . import blog

def checkBtn(false_value, form):
    if false_value in request.form and form.validate():
        return True
    else:
        return False

@blog.before_request
def before():
    if current_user.is_authenticated:
        current_user.setLastSeen()

@blog.route('/', methods=['GET', 'POST'])
def index():
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    form = PostForm()
    if request.form == "POST":
        if checkBtn("cancel", form):
            return redirect(url_for('.index'))
        elif checkBtn("submit", form):
            post = Post(title=form.title.data, body=form.body.data, author=current_user._get_current_object())
            db.session.add(post)
            db.session.commit()
            return redirect(url_for('.post', id=post.id))
    return render_template("blog/index.html", title="Blog - Home Page", year=datetime.now().year, form=form, posts=posts)

@blog.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if request.method == "POST":
        if checkBtn("cancel", form):
            pass
        elif checkBtn("submit", form):
            comment = Comment(body=form.body.data, post=post, author=current_user._get_current_object())
            db.session.add(comment)
            return redirect(url_for('.post', id=post.id) + "#comments")
    comments = post.comments.order_by(Comment.date_posted.asc())
    return render_template("blog/post.html", title="Post - " + post.title, year=datetime.now().year, post=post, form=form, comments=comments)

@blog.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    form = PostForm()
    if current_user.username != post.author.username:
        abort(403)
    if request.method == "POST":
        if checkBtn("cancel", form):
            return redirect(url_for('.post', id=id))
        elif checkBtn("submit", form):
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

@blog.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if current_user.is_authenticated:
        flash("You are already registered!")
        return redirect(url_for('.index'))
    if request.method == "POST":
        if checkBtn("cancel", form):
            return redirect(url_for('.index'))
        elif checkBtn("submit", form):
            user = User(username=form.username.data, parents_email=form.email.data, password=form.password.data)
            db.session.add(user)
            db.session.commit()
            login_user(user, False)
            flash("You have been successfully registered and logged in.")
            return redirect(url_for('.index'))
    return render_template("blog/register.html", title="Blog - Register", year=datetime.now().year, form=form)

@blog.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template("blog/profile.html", title="Blog - " + username + "'s Profile", year=datetime.now().year, user=user)

@blog.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def editProfile():
    form = EditProfile()
    if request.method == "POST":
        if checkBtn("cancel", form):
            return redirect(url_for('.profile', username=current_user.username))
        elif checkBtn("submit", form):
            current_user.about_me = form.about_me.data
            flash("Your profile has been successfully updated.")
            return redirect(url_for('.profile', username=current_user.username))
    form.about_me.data = current_user.about_me
    return render_template("blog/editProfile.html", title="Blog - Edit Your Profile", year=datetime.now().year, form=form)