from datetime import datetime
from flask import render_template, flash, redirect, request, url_for, abort, session, current_app, g
from flask_login import login_user, logout_user, current_user, login_required
from forms import LoginForm, PostForm, CommentForm, RegisterForm, EditProfile, ResetPasswordRequest, ResetPassword, SearchForm
from ..models import Comment, User, Post, Tag, db
from ..mail import send_email
from . import blog

year = datetime.now().year

def parseMultiplePost(form):
    num_list = form.tags.data
    return_list = []
    for i in num_list:
        tag = Tag.query.filter_by(id=i).first()
        return_list.append(tag)
    return return_list

def unparseMultiplePost(post):
    return_list = []
    for i in post.tags:
        tag = Tag.query.filter_by(name=i.name).first()
        return_list.append(tag.id)
    return return_list

def checkBtn(false_value, form):
    if false_value in request.form and form.validate():
        return True
    else:
        return False

@blog.before_request
def before():
    if current_user.is_authenticated:
        current_user.setLastSeen()

@blog.before_app_request
def beforeApp():
    try:
        if request.endpoint[:6] != "static" and request.endpoint != "blog.login" and request.endpoint != "blog.logout" and request.endpoint != "blog.public" and request.endpoint != "blog.draft":
            session["last_url"] = request.url
    except TypeError:
        pass
    g.tag = Tag
    g.post = Post
    g.current_user = current_user
    g.db = db

@blog.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get("page", 1, type=int)
    post_form = PostForm()
    search_form = SearchForm()
    pagination = Post.query.order_by(Post.date_posted.desc()).paginate(
        page, per_page=current_app.config["ITEMS_PER_PAGE"],
        error_out=True)
    posts = pagination.items
    if post_form.validate_on_submit():
        tags = parseMultiplePost(post_form)
        post = Post(title=post_form.title.data, body=post_form.body.data, author=current_user._get_current_object(), tags=tags, published=post_form.published.data)
        post.changedBody()
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.post', id=post.id))
    elif search_form.validate_on_submit():
        return redirect(url_for('.filteredPosts', q=search_form.search.data))
    return render_template("blog/index.html", title="Blog - Home Page", year=year, post_form=post_form, search_form=search_form, posts=posts, pagination=pagination)

@blog.route('/filtered-posts', methods=['GET', 'POST'])
def filteredPosts():
    page = request.args.get("page")
    q = request.args.get("q")
    post_form = PostForm()
    search_form = SearchForm()
    if post_form.validate_on_submit():
        tags = parseMultiplePost(post_form)
        post = Post(title=post_form.title.data, body=post_form.body.data, author=current_user._get_current_object(), tags=tags, published=post_form.published.data)
        post.changedBody()
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.post', id=post.id))
    elif search_form.validate_on_submit():
        return redirect(url_for('.filteredPosts', q=search_form.search.data))
    pagination = Post.query.whoosh_search(q, 50).paginate(
        page, per_page=current_app.config["ITEMS_PER_PAGE"],
        error_out=True)
    posts = pagination.items
    for post in posts:
        if not post.published:
            posts.pop(-post.id)
    return render_template("blog/index.html", title="Blog - Home Page", year=year, post_form=post_form, search_form=search_form, posts=posts, pagination=pagination, filtered=True)

@blog.route('/posts/<username>')
def posts(username):
    page = request.args.get("page")
    user = User.query.filter_by(username=username).first_or_404()
    pagination = Post.query.order_by(Post.date_posted.desc()).filter_by(author=user).paginate(
        page, per_page=current_app.config["ITEMS_PER_PAGE"],
        error_out=True)
    posts = pagination.items
    return render_template("blog/someonesPosts.html", title="Blog - %s's posts" % user.username.capitalize(), year=year, posts=posts, pagination=pagination, user=user)

@blog.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    if post.published == False and post.author != current_user:
        abort(403)
    form = CommentForm()
    if request.method == "POST":
        if checkBtn("cancel", form):
            pass
        elif checkBtn("submit", form):
            comment = Comment(body=form.body.data, post=post, author=current_user._get_current_object())
            db.session.add(comment)
            return redirect(url_for('.post', id=post.id) + "#comments")
    comments = post.comments.order_by(Comment.date_posted.asc())
    return render_template("blog/post.html", title="Post - " + post.title, year=year, post=post, form=form, comments=comments)

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
            post.tags = parseMultiplePost(form)
            post.published = form.published.data
            post.changedBody()
            return redirect(url_for('.post', id=id))
    form.title.data = post.title
    form.body.data = post.body
    form.tags.data = unparseMultiplePost(post)
    form.published.data = post.published
    return render_template("blog/edit.html", title="Edit Post - " + post.title, year=year, post=post, form=form)

@blog.route('/public/<int:id>')
@login_required
def public(id):
    post = Post.query.get_or_404(id)
    if post.author.username != current_user.username:
        abort(403)
    post.published = True
    flash("Your post is now public.", 'info')
    return redirect(session["last_url"])

@blog.route('/draft/<int:id>')
@login_required
def draft(id):
    post = Post.query.get_or_404(id)
    if post.author.username != current_user.username:
        abort(403)
    post.published = False
    flash("Your post is now a draft.", 'info')
    return redirect(session["last_url"])

@blog.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = form.validate_credentials(form.user_or_email, form.password)
        if user:
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or session.get("last_url") or url_for(".index"))
        else:
            flash("You have entered something incorrectly!", 'warning')
    return render_template("blog/login.html", form=form, title="Blog - Login", year=year)

@blog.route('/logout')
@login_required
def logout():
    name = current_user.username
    logout_user()
    flash("You have been logged out of the application, " + name.capitalize() + ".", 'success')
    return redirect(request.args.get('next') or session.get("last_url") or url_for('.index'))

@blog.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if current_user.is_authenticated:
        flash("You are already registered!", 'info')
        return redirect(url_for('.index'))
    if request.method == "POST":
        if checkBtn("cancel", form):
            return redirect(url_for('.index'))
        elif checkBtn("submit", form):
            user = User(username=form.username.data, parents_email=form.email.data, password=form.password.data)
            db.session.add(user)
            db.session.commit()
            token = user.generateConfirmationToken()
            if send_email(user.parents_email, 'Confirm Your Account',
                       'confirm', user=user, token=token):
                flash("We have sent you a confirmation email.", 'info')
            login_user(user, False)
            flash("You have been successfully registered and logged in.", 'success')
            return redirect(url_for('.index'))
    return render_template("blog/register.html", title="Blog - Register", year=year, form=form)

@blog.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template("blog/profile.html", title="Blog - " + username + "'s Profile", year=year, user=user)

@blog.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def editProfile():
    form = EditProfile()
    if request.method == "POST":
        if checkBtn("cancel", form):
            return redirect(url_for('.profile', username=current_user.username))
        elif checkBtn("submit", form):
            current_user.about_me = form.about_me.data
            flash("Your profile has been successfully updated.", 'success')
            return redirect(url_for('.profile', username=current_user.username))
    form.about_me.data = current_user.about_me
    return render_template("blog/editProfile.html", title="Blog - Edit Your Profile", year=year, form=form)

@blog.route('/reset-password', methods=['GET', 'POST'])
def resetPasswordRequest():
    if current_user.is_authenticated:
        return redirect(url_for('.index'))
    form = ResetPasswordRequest()
    if request.method == "POST":
        if checkBtn("submit", form):
            user = User.query.filter_by(parents_email=form.parents_email.data).first()
            token = user.generateResetToken()
            if send_email(user.parents_email, 'Reset Your Password',
                       'resetPassword', user=user, token=token):
                flash("An email to reset your password has been sent.", 'success')
            return redirect(url_for('.login'))
    return render_template("blog/resetPasswordRequest.html", title="Blog - Reset Your Password", year=year, form=form)

@blog.route('/reset-password/<token>', methods=['GET', 'POST'])
def resetPassword(token):
    if current_user.is_authenticated:
        return redirect(url_for('.index'))
    form = ResetPassword()
    if form.validate_on_submit():
        if User.resetPassword(form.password.data, token):
            flash("Your password has been updated", 'success')
            return redirect(url_for('.login'))
        else:
            flash("The password could not be updated", 'error')
            return redirect(url_for('.resetPassword'))
    return render_template("blog/resetPassword.html", title="Blog - Reset Your Password", year=year, form=form)

@blog.route('/tags/')
def tags():
    all_tags = Tag.query.all()
    return render_template("blog/tags.html", title="Blog - Available Tags", year=year, all_tags=all_tags)

@blog.route('/tag/<int:id>')
def tag(id):
    tag = Tag.query.get_or_404(id)
    return render_template("blog/tag.html", title="Blog - %s Tag" % tag.name.capitalize(), year=year, tag=tag)