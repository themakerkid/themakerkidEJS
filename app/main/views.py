from . import main

@main.route("/")
def index():
    return "Welcome to The MAKER Kid!"