from flask import Blueprint

blog = Blueprint('blog', __name__)

import views, forms