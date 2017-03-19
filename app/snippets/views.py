from datetime import datetime
from flask import render_template, flash, redirect, request, url_for, abort, current_app
from flask_login import login_user, logout_user, current_user, login_required
from forms import SnippetForm, CommentForm, SearchForm
from ..models import SnippetComment, User, Snippet, db
from . import snippets

year = datetime.now().year

def checkBtn(false_value, form):
    if false_value in request.form and form.validate():
        return True
    else:
        return False

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
    else:
        return "a language not recognized"

@snippets.before_request
def before():
    if current_user.is_authenticated:
        current_user.setLastSeen()

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
        summary = snippet_form.body.data
        summary = summary.split(' ')
        if snippet_form.language.data == 1:
            summary = summary[:40]
        else:
            summary = summary[:80]
        summary = ' '.join(summary)
        if not summary == snippet_form.body.data:
            summary += '...'
        snippet = Snippet(title=snippet_form.title.data, body=snippet_form.body.data, author=current_user._get_current_object(), code_type_id=snippet_form.language.data, summary=summary)
        db.session.add(snippet)
        db.session.commit()
        return redirect(url_for('.snippet', id=snippet.id))
    elif search_form.validate_on_submit():
        return redirect(url_for('.filtered', q=search_form.search.data))
    return render_template("snippets/index.html", title="Code Snippets - Home Page", year=year, snippet_form=snippet_form, search_form=search_form, snippets=snippets, pagination=pagination)

@snippets.route('/filtered', methods=['GET', 'POST'])
def filtered():
    page = request.args.get('page', 1, type=int)
    snippet_form = SnippetForm()
    search_form = SearchForm()
    q = request.args.get("q")
    if snippet_form.validate_on_submit():
        snippet = Snippet(title=snippet_form.title.data, body=snippet_form.body.data, author=current_user._get_current_object())
        db.session.add(snippet)
        db.session.commit()
        return redirect(url_for('.snippet', id=post.id))
    elif search_form.validate_on_submit():
        return redirect(url_for('.filtered', q=search_form.search.data))
    pagination = Snippet.query.whoosh_search(q, 50).paginate(
        page, per_page=current_app.config["ITEMS_PER_PAGE"],
        error_out=True)
    snippets = pagination.items
    return render_template("snippets/index.html", title="Code Snippets - Home Page", year=year, snippet_form=snippet_form, search_form=search_form, snippets=snippets, pagination=pagination, filtered=True)

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

@snippets.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    snippet = Snippet.query.get_or_404(id)
    language = checkLanguage(snippet)
    form = SnippetForm()
    if current_user.username != snippet.author.username:
        abort(403)
    if request.method == "POST":
        if checkBtn("cancel", form):
            return redirect(url_for('.snippet', id=id))
        elif checkBtn("submit", form):
            snippet.title = form.title.data
            snippet.body = form.body.data
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
    return render_template("snippets/someonesSnippets.html", title="%s's Code Snippets" % user.username.capitalize(), year=year, snippets=snippets, pagination=pagination, user=user)