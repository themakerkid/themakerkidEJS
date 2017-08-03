# main/views.py - contains routes for the content part of this website
# By Benjamin Murray

# Import all the necessary libraries

# Import datetime to get current year
from datetime import datetime

# Import some helper functions to flash messages, render the Jinja2 templates, the user session and to generate dynamic urls
# Also import the request dictionary to get the search query string from the url bar
from flask import flash, redirect, render_template, request, url_for, session

# Get the current user to confirm his/her account and to check if the logged in user is unconfirmed
# Also import the login_required decorator to protect routes so that only logged in users can view it
from flask_login import current_user, login_required

# Import the main Blueprint to add routes to the application
from . import main

# Used to check whether a cancel button or a submit button was pressed
from ..blog.views import checkBtn

# Import send_email function to resend the confirmation email in case the
# original email was lost and for contact page
from ..mail import send_email

# Import all the database models for the full-text search
from ..models import Comment, Post, Snippet, SnippetComment, User, db

# SearchForm class is needed to display and handle the full-text search form and ContactForm for the contact page
from .forms import SearchForm, ContactForm

# Define a year variable to reduce the amount of repetition
year = datetime.now().year

# Display a nice 404 page to the users
@main.app_errorhandler(404)
def error_404(e):
    return render_template("404.html", title="Not Found", year=year), 404

# Display the internal server error page
@main.app_errorhandler(500)
def error_500(e):
    return render_template("500.html", title="Internal Server Error", year=year), 500

# Tell the users that they cannot do something
@main.app_errorhandler(403)
def error_403(e):
    return render_template("403.html", title="Forbidden", year=year), 403

# Template filter to check just make first letter capital
@main.app_template_filter('capitalize')
def capitalizeFirstLetter(word):
    # Get first letter
    first_letter = word[0]

    # Capitalize it
    first_letter = first_letter.upper()

    # Create new word and change first letter
    new_word = first_letter + word[1:]

    # Return capitalized word
    return new_word

@main.before_request
def before():
    if request.endpoint == "main.users" and current_user.is_authenticated:
        # If the user is logged in set their last seen to the current time
        current_user.setLastSeen()

# Check if the user is unconfirmed
@main.before_app_request
def checkConfirm():
    if current_user.is_authenticated and \
            current_user.confirmed == False and \
            request.endpoint[:5] != 'main.' and \
            request.endpoint != 'main.confirm' and \
            request.endpoint != 'blog.login' and \
            request.endpoint != 'blog.logout' and \
            request.endpoint[:6] != 'static':
        # If the user if not confirmed and the browser if not requesting the static files, login page, logout page, confirm page or the content part of
        # this website, redirect them to the unconfirmed page
        return redirect(url_for('main.unconfirmed'))


@main.route("/")
def index():
    """Renders the home page"""
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
    """Renders the Scratch learning resources page."""
    return render_template('coding/scratch/scratchLearn.html', title='Scratch - Learning Resources', year=year)

@main.route('/scratch/project')
def scratchProject():
    """Renders the Scratch 'Award Winning Project' page."""
    return render_template('coding/scratch/scratchProject.html', title='Scratch - Award Winning Project', year=year, time=year - 2015)

@main.route('/scratch/project/videos/')
def scratchProjectVideos():
    """Renders the Scratch 'Award Winning Project' videos page."""
    return render_template('coding/scratch/scratchProjectVideos.html', title='Scratch - Award Winning Project Videos - Page 1', year=year)

@main.route('/webCoding/learn')
def webCodeLearn():
    """Renders the website coding learning resources page."""
    return render_template('coding/websiteCode/learn.html', title="Website Coding - Learning Resources", year=year)

@main.route('/appInventor')
def appInventor():
    """Renders the app inventor home page."""
    return render_template('coding/appInventor/intro.html', title="App Inventor - Home", year=year)

@main.route('/appInventor/projects')
def appInventorProjects():
    """Renders the app inventor projects page."""
    return render_template('coding/appInventor/projects.html', title="App Inventor - Projects", year=year)

# The routes for raspberry pi have been taken out especially for the Eir Junior Spiders Competition but they will be put back in
# after the competition so they are being kept in this file
@main.route('/raspi')
def raspi():
    """Renders the raspberry pi home page."""
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
# End of raspberry pi routes

@main.route('/coding/sample/drawing')
def drawing():
    """Renders the khan projects drawing page."""
    return render_template('coding/khancode/static_projects.html', title="My Khan Projects", year=year)

@main.route('/coding/sample/mouseOver')
def mouseOver():
    """Renders the khan projects mouse over page."""
    return render_template('coding/khancode/mouseOverProjects.html', title="Mouse Over Projects", year=year)

@main.route('/coding/sample/animated')
def animations():
    """Renders the khan projects animations page."""
    return render_template('coding/khancode/animationProjects.html', title="Animations", year=year)

# These Getting Started routes have been taken out like the raspberry pi routes for the same reason
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
# End of Getting Started routes

@main.route('/coding/famous')
def famousCoders():
    """Renders the Famous Coders page."""
    return render_template('coding/famousCoders.html', title="Getting Started - Famous Coders", year=year)

@main.route('/maker')
def maker():
    """Renders the Maker home page."""
    return render_template('maker/intro.html', title="Maker - Home Page", year=year)

@main.route('/maker/starting')
def makeStart():
    """Renders the Maker getting started page."""
    return render_template('maker/starting.html', title="Maker - Getting Started", year=year)

# This Learning Resources page and Books has been taken out for the same reason as the Getting Started pages.
@main.route('/maker/learn')
def makeLearn():
    """Renders the Maker Learning Resources page."""
    return render_template('maker/learn.html', title="Maker - Learning Resources", year=year)

@main.route('/maker/books')
def makeBooks():
    """Renders the Maker home page."""
    return render_template('maker/books.html', title="Maker - Books", year=year)
# End of Learning Resources and Books

# Electronics has been taken out for the same reason
@main.route('/maker/electronics')
def makeElec():
    """Renders the Maker Electronics page."""
    return render_template('maker/elec.html', title="Maker - Electronics - Getting Started", year=year)
# End of Electronics

@main.route('/maker/arduino/start')
def arduinoStart():
    """Renders the Maker Arduino Getting Started page."""
    return render_template('maker/arduino/ardStart.html', title="Arduino Home", year=year)

@main.route('/maker/arduino/learn')
def arduinoLearn():
    """Renders the Maker Arduino Learning Resources page."""
    # This Learning Resources page is okay
    return render_template('maker/arduino/ardLearn.html', title="Arduino - Learning Resources", year=year)

@main.route('/maker/arduino/project')
def arduinoProject():
    """Renders the Maker Arduino Projects page."""
    return render_template('maker/arduino/ardProject.html', title="Arduino - Project Page", year=year)

@main.route('/maker/arduino/project/scroller')
def scrollerProj():
    """Renders the Scroller page."""
    return render_template('/maker/arduino/projects/scroller.html', title="Arduino - Projects - Scroller", year=year)

@main.route('/maker/famous')
def famousMakers():
    """Renders the Famous Makers page."""
    return render_template('maker/famousMakers.html', title="Maker - Famous Makers", year=year)

# The robotics page taken out for the same reason as the Getting Started and the raspberry pi pages
@main.route('/maker/robotics')
def makeRobot():
    """Renders the Maker Robotics page."""
    return render_template('maker/robot.html', title="Maker - Robotics", year=year)
# End of Robotics page

@main.route('/maker/projects')
def makeProj():
    """Renders the Maker Projects page."""
    return render_template('maker/projects.html', title="Maker - Projects", year=year)

@main.route('/maker/toys')
def makeToys():
    """Renders the Maker Cool Toys page."""
    return render_template('maker/toys.html', title="Maker - Toys", year=year)

@main.route('/maker/competitionsAndEvents')
def makeCompEv():
    """Renders the Maker Competitions and events page."""
    return render_template('maker/compEv.html', title="Maker - Compitions & Events", year=year)

# The Glossary has been taken out for the same reason
@main.route('/maker/glossary')
def makeGlossary():
    """Renders the Maker Glossary page."""
    return render_template('maker/glossary.html', title="Maker - Glossary", year=year)
# End of Maker Glossary

@main.route('/coding')
def coding():
    """Renders the Coding home page."""
    return render_template('coding/intro.html', title="Coding - Introduction", year=year)

@main.route('/coding/python/learn')
def techPyLearn():
    """Renders the Coding Python learning resources page."""
    return render_template('coding/python/learn.html', title="Coding - Python - Learning Resources", year=year)

@main.route('/coding/python/this')
def techPyThis():
    """Renders the Coding, Python about this website page."""
    return render_template('coding/python/thisWebsite.html', title="Coding - Python - This Website", year=year)

@main.route('/coding/eventsCompetitions')
def techEveComp():
    """Renders the Coding Events and Competitions page."""
    return render_template('coding/eveComp.html', title="Coding - Events & Competitions", year=year)

# The Glossary has been taken out for the same reason
@main.route('/coding/glossary')
def techGlossary():
    """Renders the Coding Glossary page."""
    return render_template('coding/glossary.html', title="Coding - Python - This Website", year=year)
# End of Coding Glossary

# Fun Toys has been taken out for the same reason as the other pages that were taken out
@main.route('/funstuff/toys')
def funToys():
    """Renders the Fun Toys page."""
    return render_template('coolToys.html', title="Fun Stuff - Cool Toys", year=year)
# End of Fun Toys

# Full-text search form
@main.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if request.method == "POST":
        if checkBtn('cancel', form):
            # Cancel btn
            # JavaScript will redirect
            pass
        # Otherwise redirect to the search resutls page
        return redirect(url_for('.searchResults', q=form.search.data))
    return render_template('search.html', title="Search", year=year, form=form)

@main.route('/search-results')
def searchResults():
    # Get the query string
    q = request.args.get("q")
    # Get results from ALL of the models. This is why we imported all of them at the start of the file
    post_results = Post.query.whoosh_search(q, 50).all()
    snippet_results = Snippet.query.whoosh_search(q, 50).all()
    comment_results = Comment.query.whoosh_search(q, 50).all()
    snippet_comment_results = SnippetComment.query.whoosh_search(q, 50).all()
    return render_template('searchResults.html', title="Search Results - " + q, year=year, post_results=post_results, snippet_results=snippet_results, comment_results=comment_results, snippet_comment_results=snippet_comment_results, q=q)

@main.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed == True:
        # Do nothing if user is already confirmed
        return redirect(url_for('blog.index'))
    if current_user.confirmAccount(token): # Try to confirm account
        # If successful
        flash("We have confirmed your account, %s!" % current_user.username.capitalize(), 'success')
        return redirect(url_for('blog.index'))
    else:
        # If not successful
        flash("The confirmation link is invalid or has expired.", 'warning')
        return redirect(url_for('blog.index'))

@main.route('/unconfirmed')
@login_required
def unconfirmed():
    if current_user.confirmed == True:
        # Redirect if user is already confirmed
        return redirect(session.get("last_url") or url_for('blog.index'))
    return render_template('unconfirmed.html', title="Unconfirmed User", year=year)

@main.route('/resend-confirmation-email')
@login_required
def resendConfirmationEmail():
    # Generate token to be sent in email
    token = current_user.generateConfirmationToken()
    if send_email(current_user.parents_email, 'Confirm Your Account',
                'confirm', user=current_user, token=token): # Try to send the email (Message is flashed from send_email function if not successful)
        # If successful, flash a message
        flash("We have sent you another confirmation email.", 'info')
    return redirect(url_for('.unconfirmed'))

@main.route('/buddies')
def users():
    # Get all the users from the database
    users = User.query.filter_by(confirmed=True).order_by(User.date_registered.asc()).all()
    return render_template('users.html', title="Buddies", year=year, users=users)

@main.route('/contact', methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        if send_email('codemakerbuddy@gmail.com', 'Contact - %s' % form.subject.data,
                      'contact', form=form):
            # If successful, flash a message
            flash("Your comment has been emailed to the owner of this site (Benjamin).", 'success')
        return redirect(session["last_url"])
    return render_template('contact.html', title="Contact Me", year=year, form=form)