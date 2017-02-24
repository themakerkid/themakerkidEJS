from datetime import datetime
from flask import render_template, flash, redirect, request, url_for, abort
from flask_login import login_user, logout_user, current_user, login_required
from forms import SnippetForm, CommentForm
from ..models import SnippetComment, User, Snippet, db
from . import snippets

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
        return "Other"

@snippets.before_request
def before():
    if current_user.is_authenticated:
        current_user.setLastSeen()

@snippets.route('/', methods=['GET', 'POST'])
def index():
    snippets = Snippet.query.order_by(Snippet.date_posted.desc()).all()
    form = SnippetForm()
    if form.validate_on_submit():
        post = Snippet(title=form.title.data, body=form.body.data, author=current_user._get_current_object(), code_type_id=form.language.data)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.snippet', id=post.id))
    return render_template("snippets/index.html", title="Code Snippets - Home Page", year=datetime.now().year, form=form, snippets=snippets)

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
    return render_template("snippets/snippet.html", title="Snippet - " + snippet.title, year=datetime.now().year, snippet=snippet, form=form, comments=comments, language=language)

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
    return render_template("snippets/edit.html", title="Edit Snippet - " + snippet.title, year=datetime.now().year, snippet=snippet, form=form, language=language)