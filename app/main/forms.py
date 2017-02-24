from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class SearchForm(FlaskForm):
    search = StringField("Search Query", validators=[DataRequired()])
    submit = SubmitField("Search", false_values="search")
    cancel = SubmitField("Cancel", false_values="cancel")