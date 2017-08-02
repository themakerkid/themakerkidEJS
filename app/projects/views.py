# projects/views.py - All the routes for the shared projects
# By Benjamin Murray

# Import datetime class to get current year
from datetime import datetime

from flask import render_template, flash, redirect, url_for, abort, current_app, request

# Protect routes so that only logged in users can see it
# and the current user to get things about the user like his/her username
from flask_login import current_user, login_required

# Import all the form classes related to the projects to display and handle the forms
from .forms import ProjectForm, CommentForm

# Import some models to gather all the content in them
from ..models import Project, ProjectComment, User, db

# Import the projects Blueprint to attach some routes to the application
from . import projects

# Stop repetition of getting current year
year = datetime.now().year

def generate_document_html(project):
    if project.vid_url:
        html = """<div class="row">
    <div class="col-sm-8 col-sm-offset-2">
        <div class="embed-responsive embed-responsive-16by9">
            <iframe class="embed-responsive-item" src="{0}" allowfullscreen></iframe>
        </div>
    </div>
</div>""".format(project.vid_url)
    else:
        html = ""
    html += """<h3>Description:</h3>
<em><div class="well">{1}</div></em>

""".format(project.title, project.description_html)
    html += """

<h3>Parts you will need:</h3>
<ol>
"""
    parts_list = project.parts.split('\n')
    for part in parts_list:
        html += "    <li>{0}</li>".format(part)
    
    html += """</ol>

"""
    steps_list = project.steps_html.split('<hr>')
    i = 1
    for step in steps_list:
        html += """<h3 class="text-success">Step {0}:</h3>
<div class="well">{1}</div>

""".format(i, step)
        i += 1
    
    html += """<h3>Code:</h3>
<div style="overflow-x:auto;">
    <button class="btn btn-default copy-btn" data-clipboard-target=".highlight" style="position:absolute; top:0; right:0; border-top-right-radius:0;">Copy to clipboard</button>
    {0}
</div>""".format(project.code_html)
    
    return html

@projects.route('/')
def index():
    if current_user.is_authenticated:
        projects = Project.query.filter(db.or_(Project.status == True, Project.author == current_user, current_user.admin())).all()
    else:
        projects = Project.query.filter_by(status=True).all()
    return render_template('projects/index.html', title="Projects", year=year, projects=projects)

@projects.route('/<username>')
def someonesProjects(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user == current_user:
        projects = Project.query.filter_by(author=user).all()
    else:
        projects = Project.query.filter_by(author=user, status=True).all()
    
    first_letter = username[0].upper()
    username = first_letter + username[1:]
    return render_template('projects/someonesProjects.html', title="Projects by {0}".format(username), year=year, projects=projects, user=user)

@projects.route('/<int:id>', methods=['GET', 'POST'])
def project(id):
    project = Project.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = ProjectComment(body=form.body.data, author=current_user._get_current_object(), project=project)
        db.session.add(comment)
        return redirect(url_for('.project', id=project.id))
    comments = project.comments.order_by(ProjectComment.date_posted.asc())
    return render_template('projects/project.html', title="Projects - {0}".format(project.title), year=year, form=form, project=project, comments=comments)

@projects.route('/edit/comment/<int:id>', methods=['GET', 'POST'])
@login_required
def editComment(id):
    # Get comment from database (if it doesn't exist return 404 code)
    comment = ProjectComment.query.filter_by(id=id).first_or_404()

    # Create form object
    form = CommentForm()

    # Issue 403 or forbidden code if user is not owner and is not administrator
    if current_user.username != comment.author.username and not current_user.admin():
        abort(403)

    # If request method is POST (form submitted)
    if form.validate_on_submit():
        # If submit was pressed, update content of comment and redirect back
        comment.body = form.body.data
        return redirect(url_for('.project', id=comment.project.id) + '#comments')
    
    # Set initial values
    form.body.data = comment.body

    return render_template('projects/editComment.html', title="Projects - Edit Comment from Project {0}".format(comment.project.title), year=year, form=form, comment=comment)

@projects.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(author=current_user._get_current_object(), title=form.title.data, description=form.description.data, vid_url=form.vid_url.data, parts=form.parts.data, steps=form.steps.data, status=form.status.data, code=form.code.data)
        project.document_html = generate_document_html(project)
        db.session.add(project)
        db.session.commit()
        return redirect(url_for('.edit', id=project.id))
    form.status.default = "0"
    form.process()
    return render_template('projects/new.html', title="Projects - New Project", year=year, form=form)

@projects.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    project = Project.query.get_or_404(id)
    if not current_user.admin() and project.author.username != current_user.username:
        abort(403)
    form = ProjectForm()
    defaultOption = int(project.status)
    if form.validate_on_submit():
        project.title = form.title.data
        project.description = form.description.data
        project.vid_url = form.vid_url.data
        project.parts = form.parts.data
        project.steps = form.steps.data
        project.status = form.status.data
        project.code = form.code.data
        project.document_html = generate_document_html(project)
        if int(form.status.data) != defaultOption and int(form.status.data) == 1:
            flash("You have now published your project! Now everyone (including users that are not logged in) can see it!", 'success')
            flash("If at any time you want to make it a Draft again, then click on Draft!", 'info')
        db.session.add(project)
        db.session.commit()
        return redirect(url_for('.edit', id=project.id))
    form.status.default = defaultOption
    form.process()
    form.title.data = project.title
    form.description.data = project.description
    form.vid_url.data = project.vid_url
    form.parts.data = project.parts
    form.steps.data = project.steps
    form.code.data = project.code
    return render_template('projects/edit.html', title="Projects - Edit Project", year=year, form=form, project=project)

@projects.route('/like/<int:id>')
@login_required
def like(id):
    project = Project.query.get_or_404(id)
    if project.id in current_user.projects_liked:
        flash("You have already liked this project before!", 'info')
        return redirect(url_for('.project', id=project.id))
    elif project.author.username == current_user.username:
        flash("You cannot like your own project!", 'info')
        return redirect(url_for('.project', id=project.id))
    else:
        project.likes += 1
        current_user.projects_liked.append(project.id)
        flash("The project has been liked!", 'success')
        return redirect(url_for('.project', id=project.id))