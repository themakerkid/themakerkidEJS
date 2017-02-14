# By Benjamin 12/02/2017
# Used Blueprint because I will be adding a forum/blog later.

# Import the necessary libraries
from flask import Flask
from app.main import main as main_blueprint
from app import app, manager

# Register the blueprint with the application
app.register_blueprint(main_blueprint)

if __name__ == '__main__':
    # Run the application
    manager.run()