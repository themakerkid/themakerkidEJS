# By Benjamin 12/02/2017 - today

# Import the necessary libraries
from flask import Flask
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_whooshalchemy import whoosh_index
from app import create_app, db
from app.models import *

# Get the app
app = create_app()

# Create the manager for command line arguments and with added options
manager = Manager(app)

# Initialise Flask-Migrate and cli cmd
migrate = Migrate(app, db)
manager.add_command("db", MigrateCommand)

# Make indices on models for a Full-text Whoosh search!
whoosh_index(app, Post)
whoosh_index(app, Comment)
whoosh_index(app, Snippet)
whoosh_index(app, SnippetComment)

if __name__ == '__main__':
    # Run the application
    manager.run()