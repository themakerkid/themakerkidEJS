# blog/views.py - All the routes for the blog
# By Benjamin Murray

# Import datetime class to get current year
from datetime import datetime

# Import the template rendering, redirecting, dynamic url generator and the aborting with a status code function
# Also import the request and session dictionary to check the endpoint and to save things globally respectively
# Import the flask global to share the Tag and Post models, the current user and the database object to the macros
from flask import render_template, flash, redirect, request, url_for, abort, session, current_app, g

# Import authentication related things to login and logout users, protect routes so that only logged in users can see it
# and the current user to get things about the user like his/her username
from flask_login import login_user, logout_user, current_user, login_required

# Import all the form classes related to the blog to display and handle the forms
from forms import LoginForm, PostForm, CommentForm, RegisterForm, EditProfile, ResetPasswordRequest, ResetPassword, SearchForm

# Import some models to gather all the content in them
from ..models import Comment, User, Post, Tag, db

# Used to send confirmation email at registration
from ..mail import send_email

# Import the blog Blueprint to attach some routes to the application
from . import blog

# Stop repetition of getting current year
year = datetime.now().year

# Get Tag objects from a list of Tag ids
def parseMultiplePost(form):
    # Gather ids
    num_list = form.tags.data

    # Set initial value of list of Tag objects
    return_list = []

    # Iterate through whole list of ids
    for i in num_list:
        # Turn id into an object
        tag = Tag.query.filter_by(id=i).first()

        # Add that on to the list of Tag objects
        return_list.append(tag)
    
    # Return the list of objects back to the caller
    return return_list

# Do the reverse of the above
def unparseMultiplePost(post):
    # Set initial value of list of Tag ids
    return_list = []

    # Iterate through the list of objects
    for i in post.tags:
        # Add the id of the tag to the list of ids
        return_list.append(i.id)
    
    # Return the list of ids back to the caller
    return return_list

def checkBtn(false_value, form, validation=True):
    if validation:
        if false_value in request.form and form.validate(): # Check that the false value (a value associated with a submit button) on the button is the false value
                                                            # that was given and that the form validates
            return True
        else: # If one thing fails
            return False
    else:
        # No validation (Login Form)
        if false_value in request.form:
            return True
        else:
            return False

@blog.before_request
def before():
    if current_user.is_authenticated:
        # If the user is logged in set their last seen to the current time
        current_user.setLastSeen()

@blog.before_app_request
def beforeApp():
    try:
        if request.endpoint[:6] != "static" and request.endpoint != "blog.login" and request.endpoint != "blog.logout" and request.endpoint != "blog.public" and request.endpoint != "blog.draft" \
                and request.endpoint != "main.unconfirmed":
            # Set the last_url in the session so that routes can redirect back to the last page.
            # Routes that use last_url cannot change this (because it would otherwise be redirecting back to itself)
            session["last_url"] = request.url
    except TypeError:
        # A TypeError is thrown by Flask when the dynamic part of a url is missing (for example static files) so do nothing
        pass

    # Set some classes and variables into Flask's global so that the macros can access them (app_context_processor or context_processor doesn't work)
    g.tag = Tag
    g.post = Post
    g.current_user = current_user
    g.db = db

# Index page
@blog.route('/', methods=['GET', 'POST'])
def index():
    # Get the pagination page. If no page is specified the default page number (1) is used.
    page = request.args.get("page", 1, type=int)

    # Create the form objects
    post_form = PostForm()
    search_form = SearchForm()

    # Create a pagination object to add pagination
    pagination = Post.query.order_by(Post.date_posted.desc()).paginate(
        page, per_page=current_app.config["ITEMS_PER_PAGE"],
        error_out=True)

    # Get the Post objects out of the paginated results
    posts = pagination.items

    # If the 'Create A New Post' form is submitted and validates
    if post_form.validate_on_submit():
        # Get the actual tag objects by parsing the ids using a function that I defined earlier
        tags = parseMultiplePost(post_form)

        # Create a post object
        post = Post(title=post_form.title.data, body=post_form.body.data, author=current_user._get_current_object(), tags=tags, published=post_form.published.data)

        # Update the summary (first 80 words). The summary is displayed on the home page.
        post.changedBody()

        # Add the post to the database session
        db.session.add(post)

        # Commit the database session to write the post to the database
        db.session.commit()

        # Issue a redirect to the Post's own page (summary is not shown on that page because only one post is shown on that page)
        return redirect(url_for('.post', id=post.id))

    # If the search form is submitted
    elif search_form.validate_on_submit():
        # Issue a redirect to a routes with the exact same page except it showes filtered posts
        return redirect(url_for('.filteredPosts', q=search_form.search.data))
    
    # Render the blog/index.html template
    return render_template("blog/index.html", title="Blog - Home Page", year=year, post_form=post_form, search_form=search_form, posts=posts, pagination=pagination)

# Exact same as the index page except it searches the database with a search query
@blog.route('/filtered-posts', methods=['GET', 'POST'])
def filteredPosts():
    # Get pagination page
    page = request.args.get("page")

    # Get search query
    q = request.args.get("q")

    # Create form objects
    post_form = PostForm()
    search_form = SearchForm()

    # Do the exact same as the index page
    if post_form.validate_on_submit():
        tags = parseMultiplePost(post_form)
        post = Post(title=post_form.title.data, body=post_form.body.data, author=current_user._get_current_object(), tags=tags, published=post_form.published.data)
        post.changedBody()
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.post', id=post.id))
    elif search_form.validate_on_submit():
        return redirect(url_for('.filteredPosts', q=search_form.search.data))
    
    # This bit is slightly different
    # Search the database using Whoosh and paginate the results
    pagination = Post.query.whoosh_search(q, 50).paginate(
        page, per_page=current_app.config["ITEMS_PER_PAGE"],
        error_out=True)

    # Get the Post objects out of the paginated results
    posts = pagination.items

    # Create a counter that is needed for he loop before
    # (cannot do this is loop because you can't loop through a list of numbers
    #  and a list of Post objects)
    i = 0

    # Iterate through the list of filtered posts
    for post in posts:
        # If the post is not published and the post author isn't the logged in user
        # (authors of private posts can only see their private posts (or drafts))
        if current_user.is_authenticated:
            if not post.published and post.author.username != current_user.username and not current_user.admin():
                # Delete it from the list
                # Use counter variable to get the right index.
                posts.pop(i)
        # Increase the counter variable for the next iteration
        i += 1
    # Render the template as in the index route above but add another template variable
    # called filtered so that the template knows that it is the filtered posts.
    return render_template("blog/index.html", title="Blog - Home Page", year=year, post_form=post_form, search_form=search_form, posts=posts, pagination=pagination, filtered=True)

# Look at someone else's posts alone
@blog.route('/posts/<username>')
def posts(username):
    # Get pagination page.
    page = request.args.get("page")

    # Get the user from the database and if the username doesn't exist,
    # return a 404 error code.
    user = User.query.filter_by(username=username).first_or_404()

    # Create pagination object.
    pagination = Post.query.order_by(Post.date_posted.desc()).filter_by(author=user).paginate(
        page, per_page=current_app.config["ITEMS_PER_PAGE"],
        error_out=True)

    # Get the Post objects out of the paginated results
    posts = pagination.items

    # Render a template that is like the index page but slightly different (no search)
    return render_template("blog/someonesPosts.html", title="Blog - %s's posts" % user.username.capitalize(), year=year, posts=posts, pagination=pagination, user=user)

# Render a full post on its own
@blog.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    # Retrieve the post and if id doesn't exist yet, return a 404 status code.
    post = Post.query.get_or_404(id)
    
    # If the post isn't public and the author is not the current user
    if post.published == False and post.author != current_user and not current_user.admin():
        # Return a 403 status code (forbidden)
        abort(403)

    # Create a Comment for object
    form = CommentForm()

    # If a form is submitted (method will be POST)
    if request.method == "POST":
        if checkBtn("cancel", form):
            # If cancel button is pressed, JavaScript will hide comment form
            # (it's in a kind of accordion)
            pass
        elif checkBtn("submit", form):
            # If the Save button is pressed, save comment to database
            comment = Comment(body=form.body.data, post=post, author=current_user._get_current_object())

            # Add comment to database (database will be committed at end of each request)
            # The reason I committed the database manually above is because I needed to retrive
            # the id of it (id doesn't exist until database is committed)
            db.session.add(comment)

            # Issue redirect to same page (last method used must be GET)
            return redirect(url_for('.post', id=post.id) + "#comments")
    # Retrieve the post's comments
    comments = post.comments.order_by(Comment.date_posted.asc())

    # Render template
    return render_template("blog/post.html", title="Post - " + post.title, year=year, post=post, form=form, comments=comments)

# Editing a post
@blog.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required        # Protect the route so that only logged in users can view it
def edit(id):
    # Retrieve post from database (issue 404 error is post doesn't exist)
    post = Post.query.get_or_404(id)

    # Create form object
    form = PostForm()

    # Issue a 403 (forbidden) error if post author is not the logged in user
    if current_user.username != post.author.username and not current_user.admin():
        abort(403)

    # If request method is POST (a form was submitted)
    if request.method == "POST":
        if checkBtn("cancel", form):
            # If cancel button was pressed
            # Redirect the user to the page with the post in it
            return redirect(url_for('.post', id=id))
        elif checkBtn("submit", form):
            # If the submit button was pressed, update post
            post.title = form.title.data
            post.body = form.body.data
            post.tags = parseMultiplePost(form)
            post.published = form.published.data

            # Update the summary (first 80 words)
            post.changedBody()

            # Redirect the user to the page with the post in it
            return redirect(url_for('.post', id=id))
    
    # Set initial values of the fields with the post data
    form.title.data = post.title
    form.body.data = post.body

    # Get list of tag ids by calling the unparseMultiplePost function (it was defined earlier)
    form.tags.data = unparseMultiplePost(post)
    form.published.data = post.published

    # Render edit page template
    return render_template("blog/edit.html", title="Edit Post - " + post.title, year=year, post=post, form=form)

# Editing a comment
@blog.route('/edit/comment/<int:id>', methods=["GET", "POST"])
@login_required
def editComment(id):
    # Get comment from database (if it doesn't exist return 404 code)
    comment = Comment.query.filter_by(id=id).first_or_404()

    # Create form object
    form = CommentForm()

    # Issue 403 or forbidden code if user is not owner and is not administrator
    if current_user.username != comment.author.username and not current_user.admin():
        abort(403)
    
    # If request method is POST (form submitted)
    if request.method == "POST":
        if checkBtn("cancel", form):
            # If cancel btn was pressed, return redirect to comment's post (don't forget to go to comments part of the post)
            return redirect(url_for('.post', id=comment.post.id) + '#comments')
        elif checkBtn("submit", form):
            # If submit was pressed, update content of comment and redirect back
            comment.body = form.body.data
            return redirect(url_for('.post', id=comment.post.id) + '#comments')
    
    # Set initial values
    form.body.data = comment.body

    # Render template
    return render_template("blog/editComment.html", title="Edit Comment for post " + comment.post.title, year=year, comment=comment, form=form)

# Make a post public
@blog.route('/public/<int:id>')
@login_required        # Protect the route so that only logged in users can view it
def public(id):
    # Retrieve post from database (issue 404 error is post doesn't exist)
    post = Post.query.get_or_404(id)

    # Issue a 403 (forbidden) error if post author is not the logged in user
    if post.author.username != current_user.username and not current_user.admin():
        abort(403)

    # Change status of post
    post.published = True

    # Flash a message that says that the post is public.
    flash("Your post is now public.", 'info')

    # Issue a redirect to the page that requested this page.
    return redirect(session["last_url"])

# Make a post private or a draft
@blog.route('/draft/<int:id>')
@login_required        # Protect the route so that only logged in users can view it
def draft(id):
    # Retrieve post from database (issue 404 error is post doesn't exist)
    post = Post.query.get_or_404(id)

    # Issue a 403 (forbidden) error if post author is not the logged in user
    if post.author.username != current_user.username and not current_user.admin():
        abort(403)

    # Change status of post
    post.published = False

    # Flash a message that says that the post is a draft
    flash("Your post is now a draft.", 'info')

    # Issue a redirect to the page that requested this page.
    return redirect(session["last_url"])

# Login route
@blog.route('/login', methods=["GET", "POST"])
def login():
    # Create form object
    form = LoginForm()

    # If form validates on submit
    if form.validate_on_submit():
        if checkBtn("cancel", form):
            # If cancel button is pressed
            if request.args.get("next"):
                flash("You must login to visit that page.", "info")
                return redirect(url_for(".login", next=request.args["next"]))
            else:
                return redirect(session.get("last_url") or url_for(".index"))
        elif checkBtn("submit", form):
            # If submit button is pressed
            # Login the user
            login_user(form.user, form.remember_me.data)

            # Issue a redirect to:
            # 1. If a user visited a protected route, redirect them back to that url
            # 2. the last url, if it exists in session
            # 3. otherwise redirect to index page
            return redirect(request.args.get('next') or session.get("last_url") or url_for(".index"))
    # Render template
    return render_template("blog/login.html", form=form, title="Blog - Login", year=year)

# Logout route
@blog.route('/logout')
@login_required        # Protect the route so that only logged in users can view it
def logout():
    # Get username of logged in user so that it can be used in flash message
    name = current_user.username

    # Logout the logged in user
    logout_user()

    # Flash message with their username.
    flash("You have been logged out of the application, " + name.capitalize() + ".", 'success')
    return redirect(request.args.get('next') or session.get("last_url") or url_for('.index'))

# Registration
@blog.route('/register', methods=["GET", "POST"])
def register():
    # Create form object
    form = RegisterForm()

    # If user is logged in
    if current_user.is_authenticated:
        # flash a message saying that they are already registered
        flash("You are already registered!", 'info')

        # Issue a redirect
        return redirect(url_for('.index'))

    # If request method is POST (the form was submitted)
    if request.method == "POST":
        if checkBtn("cancel", form):
            # If cancel button was pressed, issue a redirect
            return redirect(url_for('.index'))
        elif checkBtn("submit", form):
            # If submit button was pressed, create and add the user details to database
            user = User(username=form.username.data, parents_email=form.email.data, password=form.password.data)
            db.session.add(user)

            # Commit manually to login the user
            db.session.commit()

            # Generate token to be sent in confirmation email
            token = user.generateConfirmationToken()
            if send_email(user.parents_email, 'Confirm Your Account',
                       'confirm', user=user, token=token):
                # If successful, flash a green message (below).
                # If not successful flash a red message (in send_email function).
                flash("We have sent you a confirmation email.", 'info')
            # Login user
            login_user(user, False)


            # Flash a message
            flash("You have been successfully registered and logged in.", 'success')

            # Issue a redirect
            return redirect(url_for('.index'))
    # Render template
    return render_template("blog/register.html", title="Blog - Register", year=year, form=form)

# User profile
@blog.route('/profile/<username>')
def profile(username):
    # Retrieve user from database
    user = User.query.filter_by(username=username).first_or_404()

    # Render template
    return render_template("blog/profile.html", title="Blog - " + username + "'s Profile", year=year, user=user)

# Edit logged in user's profile
@blog.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def editProfile():
    # Create form object
    form = EditProfile()

    # If request method is POST (the form was submitted)
    if request.method == "POST":
        if checkBtn("cancel", form):
            # If cancel button is pressed, issue a redirect to profile page
            return redirect(url_for('.profile', username=current_user.username))
        elif checkBtn("submit", form):
            # If submit button is pressed, update about me.
            current_user.about_me = form.about_me.data

            # Flash message
            flash("Your profile has been successfully updated.", 'success')

            # Issue redirect
            return redirect(url_for('.profile', username=current_user.username))
    # Set initial value
    form.about_me.data = current_user.about_me

    # Render template
    return render_template("blog/editProfile.html", title="Blog - Edit Your Profile", year=year, form=form)

# Edit a user's profile (admin)
@blog.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
def editProfileAdmin(id):
    # Retrieve user or 404 code
    user = User.query.get_or_404(id)
    
    if current_user.username != user.username and not current_user.admin():
        abort(403)
    # Create form object
    form = EditProfile()

    # If request method is POST (the form was submitted)
    if request.method == "POST":
        if checkBtn("cancel", form):
            # If cancel button is pressed, issue a redirect to profile page
            return redirect(url_for('.profile', username=user.username))
        elif checkBtn("submit", form):
            # If submit button is pressed, update about me.
            user.about_me = form.about_me.data

            # Flash message
            flash("The profile has been successfully updated.", 'success')

            # Issue redirect
            return redirect(url_for('.profile', username=user.username))
    # Set initial value
    form.about_me.data = user.about_me

    # Render template
    return render_template("blog/editProfile.html", title="Blog - User's Profile", year=year, form=form, user=user)

# Reset password, getting email
@blog.route('/reset-password', methods=['GET', 'POST'])
def resetPasswordRequest():
    if current_user.is_authenticated:
        # If user is already logged in (they have their password), issue a redirect
        return redirect(url_for('.index'))
    
    # Create form object
    form = ResetPasswordRequest()

    # If request method is POST (the form is submitted)
    if request.method == "POST":
        if checkBtn("submit", form):
            # If submit button is pressed, send reset email with token
            user = User.query.filter_by(parents_email=form.parents_email.data).first()
            token = user.generateResetToken()
            if send_email(user.parents_email, 'Reset Your Password',
                       'resetPassword', user=user, token=token):
                # If successful, flash green message
                flash("An email to reset your password has been sent.", 'success')
            # Issue redirect to login page
            return redirect(url_for('.login'))
    # Render template
    return render_template("blog/resetPasswordRequest.html", title="Blog - Reset Your Password", year=year, form=form)

# Reset password, link in email has been clicked
@blog.route('/reset-password/<token>', methods=['GET', 'POST'])
def resetPassword(token):
    if current_user.is_authenticated:
        # If user is already logged in (they have their password), issue a redirect
        return redirect(url_for('.index'))
    # Create form object
    form = ResetPassword()

    # If the form validates on submit
    if form.validate_on_submit():
        if User.resetPassword(form.password.data, token):
            # If the password reset is successful, flash green message
            flash("Your password has been updated", 'success')
            # Issue redirect to login page
            return redirect(url_for('.login'))
        else:
            # If not successful, flash red message
            flash("The password could not be updated", 'error')

            # Issue redirect to this page
            return redirect(url_for('.resetPassword'))
    # Render template
    return render_template("blog/resetPassword.html", title="Blog - Reset Your Password", year=year, form=form)

# List all tags
@blog.route('/tags/')
def tags():
    # Get all tags
    all_tags = Tag.query.all()

    # Render template
    return render_template("blog/tags.html", title="Blog - Available Tags", year=year, all_tags=all_tags)

# List a tag with its posts
@blog.route('/tag/<int:id>')
def tag(id):
    # Retrieve tag
    tag = Tag.query.get_or_404(id)

    # Render template
    return render_template("blog/tag.html", title="Blog - %s Tag" % tag.name.capitalize(), year=year, tag=tag)