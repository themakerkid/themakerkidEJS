from datetime import datetime
from flask import render_template, flash, redirect, request, url_for
from flask_login import login_user, logout_user, current_user, login_required
from forms import LoginForm
from wtforms import ValidationError
from ..models import User, db
from . import blog

@blog.route('/')
def index():
    return render_template('blog/index.html', title="Blog - Home Page", year=datetime.now().year)

@blog.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.validate_credentials(form.user_or_email, form.password):
            user = User.query.filter(db.or_(User.username==form.user_or_email.data, User.parents_email==form.user_or_email.data)).first()
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