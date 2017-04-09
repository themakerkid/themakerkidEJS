# Benjamin 12/02/2017 and 13/02/2017

# App must be created here because
# templates and static folders must
# be in the same folder as the file
# that creates the app.

# Import necessary libraries
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import os

# Create the Bootstrap object to add the bootstrap folder (venv/Lib/site-packages/flask_bootstrap/templates/bootstrap/) to the templates
bootstrap = Bootstrap()

# Create Login Manager object
login = LoginManager()
login.session_protection = 'strong' # Set the Session Protection (basic or strong)
login.login_view = 'blog.login'
login.login_message_category = 'info'

# Create the Database object
db = SQLAlchemy()

# Create the Moment object (for calculating time)
moment = Moment()

# Create the Mail object (obviously for sending email)
mail = Mail()

def create_app():
    # Create app
    app = Flask(__name__)

    # Configure everything
    app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///../tmk.sqlite'
    # app.config["SQLALCHEMY_DATABASE_URI"] = mysql://username:password@localhost:3306/tmk
    app.config["SQLALCHEMY_COMMIT_ON_TEARDOWN"] = True
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or "\xee#\xe7\xf9\xba\xef8\xe9@vvq\x13\xd1\xe8\xf8\xaa\xb4\x05\xaa\x04\x16\xac\xfa"
    app.config["ITEMS_PER_PAGE"] = 10
    app.config["MAIL_SERVER"] = 'smtp.gmail.com'
    app.config["MAIL_PORT"] = 465
    app.config["MAIL_USE_SSL"] = True
    app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
    app.config["RECAPTCHA_USE_SSL"] = False
    app.config["RECAPTCHA_PUBLIC_KEY"] = os.environ.get("RECAPTCHA_PUBLIC")
    app.config["RECAPTCHA_PRIVATE_KEY"] = os.environ.get("RECAPTCHA_PRIVATE")
    app.debug = True

    # Initialise all the extensions
    bootstrap.init_app(app)
    login.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    moment.init_app(app)

    # Register the blueprints with the application
    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)


    from app.blog import blog as blog_blueprint
    app.register_blueprint(blog_blueprint, url_prefix='/blog')

    from app.snippets import snippets as snippets_bluprint
    app.register_blueprint(snippets_bluprint, url_prefix='/snippets')

    return app
