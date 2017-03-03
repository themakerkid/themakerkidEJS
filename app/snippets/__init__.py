from flask import Blueprint

snippets = Blueprint('snippets', __name__)

import views, forms

@snippets.context_processor
def injectLanguage():
    return dict(checkLanguage=views.checkLanguage)