from datetime import datetime
from flask import render_template
from . import blog

@blog.route('/')
def index():
    return render_template('blog/index.html', title="Blog - Home Page", year=datetime.now().year)