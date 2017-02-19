# Benjamin 12/02/2017 and 13/02/2017

# App must be created here because
# templates and static folders must
# be in the same folder as the file
# that creates the app.

# Import necessary libraries
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import os

basedir = 'C:/projects/themakerkidEJS'

# Create the Bootstrap object to add the bootstrap folder (venv/Lib/site-packages/flask_bootstrap/templates/bootstrap/) to the templates
bootstrap = Bootstrap()

# Create Login Manager object
login = LoginManager()
login.session_protection = 'strong' # Set the Session Protection (basic or strong)
login.login_view = 'blog.login'

# Create the Database object
db = SQLAlchemy()

# Create the Moment object (for calculating time)
moment = Moment()

def create_app():
    # Create app
    app = Flask(__name__)

    # Configure everything
    app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(basedir, "tmk.sqlite")
    app.config["SQLALCHEMY_COMMIT_ON_TEARDOWN"] = True
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or "\xee#\xe7\xf9\xba\xef8\xe9@vvq\x13\xd1\xe8\xf8\xaa\xb4\x05\xaa\x04\x16\xac\xfa"

    # Initialise all the extensions
    bootstrap.init_app(app)
    login.init_app(app)
    db.init_app(app)
    moment.init_app(app)

    return app