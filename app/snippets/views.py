# snippets/views.py - views for the snippets blueprint
# By Benjamin Murray

# Import datetime to get current year
from datetime import datetime

# Import some built-in flask functions and dictonaries
from flask import render_template, flash, redirect, request, url_for, abort, current_app, session

# Import logged-in user and route protector
from flask_login import current_user, login_required

# Import form classes
from forms import SnippetForm, CommentForm, SearchForm

# Import models to create some comment and snippets
from ..models import SnippetComment, User, Snippet, db

# Import blueprint
from . import snippets

# Stop repetition
year = datetime.now().year

# Check which button has been pressed
def checkBtn(false_value, form):
    if false_value in request.form and form.validate():
        return True
    else:
        return False

# Check which language a snippet has from an id
def checkLanguage(snippet):
    if snippet.code_type_id == 1:
        return "HTML"
    elif snippet.code_type_id == 2:
        return "CSS"
    elif snippet.code_type_id == 3:
        return "JavaScript"
    elif snippet.code_type_id == 4:
        return "Arduino C++"
    elif snippet.code_type_id == 5:
        return "Python"
    elif snippet.code_type_id == 6:
        return "Processing.js"
    elif snippet.code_type_id == 7:
        return "SQL"
    else:
        return "Other"

# Set last seen for logged-in user
@snippets.before_request
def before():
    if current_user.is_authenticated:
        current_user.setLastSeen()

# Index route
@snippets.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Snippet.query.order_by(Snippet.date_posted.desc()).paginate(
        page, per_page=current_app.config["ITEMS_PER_PAGE"],
        error_out=True)
    snippets = pagination.items
    snippet_form = SnippetForm()
    search_form = SearchForm()
    if snippet_form.validate_on_submit():
        # Create snippet
        snippet = Snippet(title=snippet_form.title.data, body=snippet_form.body.data, author=current_user._get_current_object(), code_type_id=snippet_form.language.data)

        # Update summary
        snippet.changedBody()
        db.session.add(snippet)
        db.session.commit()
        return redirect(url_for('.snippet', id=snippet.id))
    elif search_form.validate_on_submit():
        session["language"] = search_form.language_used
        session["search_query"] = search_form.search_query
        session["language_id"] = search_form.language.data
        session["both"] = search_form.both
        if int(session["language_id"]) == 0:
            return redirect(url_for('.index'))
        if not search_form.search.data:
            if int(session["language_id"]) == 1:
                q = "HTML"
            elif int(session["language_id"]) == 2:
                q = "CSS"
            elif int(session["language_id"]) == 3:
                q = "JavaScript"
            elif int(session["language_id"]) == 4:
                q = "Arduino C++"
            elif int(session["language_id"]) == 5:
                q = "Python"
            elif int(session["language_id"]) == 6:
                q = "Processing"
            else:
                q = "Other"
        else:
            q = search_form.search.data
        return redirect(url_for('.filtered', q=q))
    return render_template("snippets/index.html", title="Code Snippets - Home Page", year=year, snippet_form=snippet_form, search_form=search_form, snippets=snippets, pagination=pagination)

# Same as above but with models being searched
@snippets.route('/filtered', methods=['GET', 'POST'])
def filtered():
    if not session.get("language", False) and not session.get("search_query", False) and not session.get("language_id", False) and not session.get("both", False):
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    snippet_form = SnippetForm()
    search_form = SearchForm()
    q = request.args.get("q")
    if snippet_form.validate_on_submit():
        snippet = Snippet(title=snippet_form.title.data, body=snippet_form.body.data, author=current_user._get_current_object())
        snippet.changedBody()
        db.session.add(snippet)
        db.session.commit()
        return redirect(url_for('.snippet', id=post.id))
    elif search_form.validate_on_submit():
        session["language"] = search_form.language_used
        session["search_query"] = search_form.search_query
        session["language_id"] = search_form.language.data
        session["both"] = search_form.both
        if int(session["language_id"]) == 0:
            return redirect(url_for('.filtered', q=q))
        if not search_form.search.data:
            if int(session["language_id"]) == 1:
                q = "HTML"
            elif int(session["language_id"]) == 2:
                q = "CSS"
            elif int(session["language_id"]) == 3:
                q = "JavaScript"
            elif int(session["language_id"]) == 4:
                q = "Arduino C++"
            elif int(session["language_id"]) == 5:
                q = "Python"
            elif int(session["language_id"]) == 6:
                q = "Processing"
            else:
                q = "Other"
        else:
            q = search_form.search.data
        return redirect(url_for('.filtered', q=q))
    if session["both"]:
        pagination = Snippet.query.whoosh_search(q, 50).filter_by(code_type_id=int(session.get("language_id"))).paginate(
            page, per_page=current_app.config["ITEMS_PER_PAGE"],
            error_out=True)
    elif session["search_query"]:
        pagination = Snippet.query.whoosh_search(q, 50).paginate(
            page, per_page=current_app.config["ITEMS_PER_PAGE"],
            error_out=True)
    elif session["language"]:
        pagination = Snippet.query.filter_by(code_type_id=int(session.get("language_id"))).paginate(
            page, per_page=current_app.config["ITEMS_PER_PAGE"],
            error_out=True)
    snippets = pagination.items
    return render_template("snippets/index.html", title="Code Snippets - Home Page", year=year, snippet_form=snippet_form, search_form=search_form, snippets=snippets, pagination=pagination, filtered=True)

# Individual snippet
@snippets.route('/<int:id>', methods=['GET', 'POST'])
def snippet(id):
    snippet = Snippet.query.get_or_404(id)
    form = CommentForm()
    language = checkLanguage(snippet)
    if request.method == "POST":
        if checkBtn("cancel", form):
            pass
        elif checkBtn("submit", form):
            comment = SnippetComment(body=form.body.data, snippet=snippet, author=current_user._get_current_object())
            db.session.add(comment)
            return redirect(url_for('.snippet', id=snippet.id) + "#comments")
    comments = snippet.comments.order_by(SnippetComment.date_posted.asc())
    return render_template("snippets/snippet.html", title="Snippet - " + snippet.title, year=year, snippet=snippet, form=form, comments=comments, language=language)

# Editing a snippet
@snippets.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    snippet = Snippet.query.get_or_404(id)
    language = checkLanguage(snippet)
    form = SnippetForm()
    if current_user.username != snippet.author.username and not current_user.admin():
        abort(403)
    if request.method == "POST":
        if checkBtn("cancel", form):
            return redirect(url_for('.snippet', id=id))
        elif checkBtn("submit", form):
            snippet.title = form.title.data
            snippet.body = form.body.data
            snippet.code_type_id = form.language.data
            snippet.changedBody()
            return redirect(url_for('.snippet', id=id))
    form.title.data = snippet.title
    form.body.data = snippet.body
    form.language.data = snippet.code_type_id
    return render_template("snippets/edit.html", title="Edit Snippet - " + snippet.title, year=year, snippet=snippet, form=form, language=language)

# Someone's snippets
@snippets.route('/<username>')
def someonesSnippets(username):
    # Get pagination
    page = request.args.get("page", 1, type=int)

    # Get user (if user does not exist, return 404 code)
    user = User.query.filter_by(username=username).first_or_404()

    # Create pagination
    pagination = Snippet.query.order_by(Snippet.date_posted.desc()).filter_by(author=user).paginate(
        page, per_page=current_app.config["ITEMS_PER_PAGE"],
        error_out=True)
    
    # Get snippets out of pagination
    snippets = pagination.items

    # Render template
    first_letter = username[0].upper()
    username = first_letter + username[1:]
    return render_template("snippets/someonesSnippets.html", title="%s's Code Snippets" % username, year=year, snippets=snippets, pagination=pagination, user=user)