# By Benjamin 12/02/2017 - today
# This is all the routes for the app.

from datetime import datetime
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from . import main
from ..blog.views import checkBtn
from ..mail import send_email
from ..models import Comment, Post, Snippet, SnippetComment, User, db
from .forms import SearchForm

year = datetime.now().year

@main.app_errorhandler(404)
def error_404(e):
    return render_template("404.html", title="Not Found", year=year), 404

@main.app_errorhandler(500)
def error_500(e):
    return render_template("500.html", title="Internal Server Error", year=year), 500

@main.app_errorhandler(403)
def error_403(e):
    return render_template("403.html", title="Forbidden", year=year), 403

@main.before_app_request
def checkConfirm():
    if current_user.is_authenticated and \
            current_user.confirmed == False and \
            request.endpoint[:5] != 'main.' and \
            request.endpoint != 'main.confirm' and \
            request.endpoint != 'blog.login' and \
            request.endpoint != 'blog.logout' and \
            request.endpoint[:6] != 'static':
        return redirect(url_for('main.unconfirmed'))


@main.route("/")
def index():
    return render_template("index.html", title="Home Page", year=year)

@main.route('/about')
def about():
    """Renders the about page."""
    return render_template('about.html', title='About Me', year=year)

@main.route('/scratch')
def scratch():
    """Renders the Scratch home page."""
    return render_template('coding/scratch/scratch.html', title='Scratch - Home', year=year)

@main.route('/scratch/learn')
def scratchLearn():
    """Renders the Scratch learning page."""
    return render_template('coding/scratch/scratchLearn.html', title='Scratch - Learning Resources', year=year)

@main.route('/scratch/project')
def scratchProject():
    """Renders the Scratch 'Award Winning Project' page."""
    return render_template('coding/scratch/scratchProject.html', title='Scratch - Award Winning Project', year=year, time=year - 2015)

@main.route('/scratch/project/videos/')
def scratchProjectVideos():
    """Renders the Scratch 'Award Winning Project' video page no.1."""
    return render_template('coding/scratch/scratchProjectVideos.html', title='Scratch - Award Winning Project Videos - Page 1', year=year)

@main.route('/processing')
def processing():
    """Renders the khan projects page."""
    return render_template('coding/processing/gettingStarted.html', title="Processing - Getting Started", year=year)

@main.route('/processing/learn')
def processingLearn():
    """Renders the khan projects page."""
    return render_template('coding/processing/learn.html', title="Processing - Learning Resources", year=year)

@main.route('/webCoding')
def websiteCoding():
    """Renders the khan projects page."""
    return render_template('coding/websiteCode/gettingStarted.html', title="Website Coding - Home Page", year=year)

@main.route('/webCoding/learn')
def webCodeLearn():
    """Renders the khan projects page."""
    return render_template('coding/websiteCode/learn.html', title="Website Coding - Learning Resources", year=year)

@main.route('/webCoding/thisWebsite')
def webCodeThis():
    """Renders the khan projects page."""
    return render_template('coding/websiteCode/thisWebsite.html', title="Website Coding - Learning Resources", year=year)

@main.route('/appInventor')
def appInventor():
    """Renders the app inventor intro page."""
    return render_template('coding/appInventor/intro.html', title="App Inventor - Home", year=year)

@main.route('/appInventor/learn')
def appInventorLearn():
    """Renders the app inventor learning resources page."""
    return render_template('coding/appInventor/learn.html', title="App Inventor - Learning Resources", year=year)

@main.route('/appInventor/projects')
def appInventorProjects():
    """Renders the app inventor projects page."""
    return render_template('coding/appInventor/projects.html', title="App Inventor - Projects", year=year)

@main.route('/raspi')
def raspi():
    """Renders the khan projects page."""
    return render_template('coding/websiteCode/thisWebsite.html', title="Website Coding - Learning Resources", year=year)

@main.route('/raspi/learn')
def raspiLearn():
    """Renders the khan projects page."""
    return render_template('coding/websiteCode/thisWebsite.html', title="Website Coding - Learning Resources", year=year)

@main.route('/raspi/python')
def raspiPython():
    """Renders the khan projects page."""
    return render_template('coding/websiteCode/thisWebsite.html', title="Website Coding - Learning Resources", year=year)

@main.route('/raspi/codeWeb')
def raspiCode():
    """Renders the khan projects page."""
    return render_template('coding/websiteCode/thisWebsite.html', title="Website Coding - Learning Resources", year=year)

@main.route('/raspi/hardware')
def raspiHardware():
    """Renders the khan projects page."""
    return render_template('coding/websiteCode/thisWebsite.html', title="Website Coding - Learning Resources", year=year)

@main.route('/processing/khan/drawing')
def drawing():
    """Renders the khan projects page."""
    return render_template('coding/khancode/static_projects.html', title="My Khan Projects", year=year)

@main.route('/processing/khan/mouseOver')
def mouseOver():
    return render_template('coding/khancode/mouseOverProjects.html', title="Mouse Over Projects", year=year)

@main.route('/processing/khan/animations')
def animations():
    return render_template('coding/khancode/animationProjects.html', title="Animations", year=year)

@main.route('/webCoding')
def webCode():
    """Renders the khan projects page."""
    return render_template('coding/wesiteCode/gettingStarted.html', title="Website Coding - Getting Started", year=year)

@main.route('/starting')
def starting():
    return render_template('starting/intro.html', title="Getting Started - Home Page", year=year)

@main.route('/starting/books')
def startBooks():
    return render_template('starting/books.html', title="Getting Started - Books", year=year)

@main.route('/starting/events')
def startCompEvents():
    return render_template('starting/compEvent.html', title="Getting Started - Events", year=year)

@main.route('/starting/glossary')
def startGlossary():
    return render_template('starting/glossary.html', title="Getting Started - Glossary", year=year)

@main.route('/starting/learn')
def startLearn():
    return render_template('starting/learn.html', title="Getting Started - Learning Resources", year=year)

@main.route('/coding/famous')
def famousCoders():
    return render_template('coding/famousCoders.html', title="Getting Started - Famous Coders", year=year)

@main.route('/maker')
def maker():
    return render_template('maker/intro.html', title="Maker - Home Page", year=year)

@main.route('/maker/learn')
def makeLearn():
    return render_template('maker/learn.html', title="Maker - Learning Resources", year=year)

@main.route('/maker/books')
def makeBooks():
    return render_template('maker/books.html', title="Maker - Books", year=year)

@main.route('/maker/electronics')
def makeElec():
    return render_template('maker/elec.html', title="Maker - Electronics - Getting Started", year=year)

@main.route('/maker/arduino/start')
def arduinoStart():
    return render_template('maker/arduino/ardStart.html', title="Arduino Home", year=year)

@main.route('/maker/arduino/learn')
def arduinoLearn():
    return render_template('maker/arduino/ardLearn.html', title="Arduino - Learning Resources", year=year)

@main.route('/maker/arduino/project')
def arduinoProject():
    return render_template('maker/arduino/ardProject.html', title="Arduino - Project Page", year=year)

@main.route('/maker/famous')
def famousMakers():
    return render_template('maker/famousMakers.html', title="Maker - Famous Makers", year=year)

@main.route('/maker/robotics')
def makeRobot():
    return render_template('maker/robot.html', title="Maker - Robotics", year=year)

@main.route('/maker/projects')
def makeProj():
    return render_template('maker/projects.html', title="Maker - Projects", year=year)

@main.route('/maker/toys')
def makeToys():
    return render_template('maker/toys.html', title="Maker - Toys", year=year)

@main.route('/maker/competitionsAndEvents')
def makeCompEv():
    return render_template('maker/compEv.html', title="Maker - Compitions & Events", year=year)

@main.route('/maker/glossary')
def makeGlossary():
    return render_template('maker/glossary.html', title="Maker - Glossary", year=year)

@main.route('/coding')
def coding():
    return render_template('coding/intro.html', title="Coding (Basic) - Introduction", year=year)

@main.route('/coding/python')
def techPython():
    return render_template('coding/python/gettingStarted.html', title="Technology - Python - Getting Started", year=year)

@main.route('/coding/python/learn')
def techPyLearn():
    return render_template('coding/python/learn.html', title="Technology - Python - Learning Resources", year=year)

@main.route('/coding/python/this')
def techPyThis():
    return render_template('coding/python/thisWebsite.html', title="Technology - Python - This Website", year=year)

@main.route('/coding/eventsCompetitions')
def techEveComp():
    return render_template('coding/eveComp.html', title="Technology - Events & Competitions", year=year)

@main.route('/coding/glossary')
def techGlossary():
    return render_template('coding/glossary.html', title="Technology - Python - This Website", year=year)

@main.route('/funstuff/toys')
def funToys():
    return render_template('coolToys.html', title="Fun Stuff - Cool Toys", year=year)

@main.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if request.method == "POST":
        if checkBtn('cancel', form):
            pass
        return redirect(url_for('.searchResults', q=form.search.data))
    return render_template('search.html', title="Search", year=year, form=form)

@main.route('/search-results')
def searchResults():
    q = request.args.get("q")
    # Get results from ALL of the models
    post_results = Post.query.whoosh_search(q, 50).all()
    snippet_results = Snippet.query.whoosh_search(q, 50).all()
    comment_results = Comment.query.whoosh_search(q, 50).all()
    snippet_comment_results = SnippetComment.query.whoosh_search(q, 50).all()
    return render_template('searchResults.html', title="Search Results - " + q, year=year, post_results=post_results, snippet_results=snippet_results, comment_results=comment_results, snippet_comment_results=snippet_comment_results, q=q)

@main.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed == True:
        return redirect(url_for('blog.index'))
    if current_user.confirmAccount(token):
        flash("We have confirmed your account, %s!" % current_user.username.capitalize(), 'success')
        return redirect(url_for('blog.index'))
    else:
        flash("The confirmation link is invalid or has expired.", 'error')
        return redirect(url_for('blog.index'))

@main.route('/unconfirmed')
@login_required
def unconfirmed():
    if current_user.confirmed == True:
        return redirect(url_for('blog.index'))
    return render_template('unconfirmed.html', title="Unconfirmed User", year=year)

@main.route('/resend-confirmation-email')
@login_required
def resendConfirmationEmail():
    token = current_user.generateConfirmationToken()
    if send_email(current_user.parents_email, 'Confirm Your Account',
                'confirm', user=current_user, token=token):
        flash("We have sent you another confirmation email.", 'info')
    return redirect(url_for('.unconfirmed'))

@main.route('/users')
def users():
    users = User.query.all()
    return render_template('users.html', title="Registered Users", year=year, users=users)