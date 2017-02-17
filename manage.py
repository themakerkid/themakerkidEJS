# By Benjamin 12/02/2017
# Used Blueprint because I will be adding a forum/blog later.

# Import the necessary libraries
from flask import Flask
from flask_script import Manager
from app.main import main as main_blueprint
from app.blog import blog as blog_blueprint
from app import app

# Create the manager for command line arguments
manager = Manager(app)

# Register the blueprints with the application
app.register_blueprint(main_blueprint)
app.register_blueprint(blog_blueprint, url_prefix='/blog')

if __name__ == '__main__':
    # Run the application
    manager.run()