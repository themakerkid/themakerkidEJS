from flask import Blueprint

snippets = Blueprint('snippets', __name__)

import views, forms