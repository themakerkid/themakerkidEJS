# By Benjamin 12/02/2017
# Used Blueprint because I will be adding a forum/blog later.

# Import the necessary libraries
from flask import Flask
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app.main import main as main_blueprint
from app.blog import blog as blog_blueprint
from app import create_app, db
import app.models

# Get the app
app = create_app()

# Create the manager for command line arguments and with added options
manager = Manager(app)

# Initialise Flask-Migrate and cli cmd
migrate = Migrate(app, db)
manager.add_command("db", MigrateCommand)

# Register the blueprints with the application
app.register_blueprint(main_blueprint)
app.register_blueprint(blog_blueprint, url_prefix='/blog')

if __name__ == '__main__':
    # Run the application
    manager.run()