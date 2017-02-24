# By Benjamin 12/02/2017
# Used Blueprint because I will be adding a forum/blog later.

# Import the necessary libraries
from flask import Flask
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import create_app, db
import app.models

# Get the app
app = create_app()

# Create the manager for command line arguments and with added options
manager = Manager(app)

# Initialise Flask-Migrate and cli cmd
migrate = Migrate(app, db)
manager.add_command("db", MigrateCommand)

if __name__ == '__main__':
    # Run the application
    manager.run()