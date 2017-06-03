from flask import Blueprint

projects = Blueprint('projects', __name__)

import views, forms