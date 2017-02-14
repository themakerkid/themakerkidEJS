# Benjamin 12/02/2017 and 13/02/2017

# App must be created here because
# templates and static folders must
# be in the same folder as the file
# that creates the app.

# Import necessary libraries
from flask import Flask
from flask_script import Manager
from flask_bootstrap import Bootstrap

# Create app
app = Flask(__name__)

# Create the manager for command line arguments
manager = Manager(app)

# Create the Bootstrap object to add the bootstrap folder (venv/Lib/site-packages/flask_bootstrap/templates/bootstrap/) to the templates
bootstrap = Bootstrap(app)