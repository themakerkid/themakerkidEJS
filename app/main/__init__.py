from flask import Blueprint
from ..models import Tag

main = Blueprint("main", __name__)

import views

@main.app_context_processor
def inject_tags():
    return dict(Tag=Tag)