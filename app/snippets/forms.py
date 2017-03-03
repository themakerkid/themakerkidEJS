from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, ValidationError
from wtforms.validators import Length, DataRequired
from ..models import Snippet

choices = ((0, "Please select a language"), (Snippet.HTML, "HTML"), (Snippet.CSS, "CSS"), (Snippet.JAVASCRIPT, "JavaScript"), (Snippet.ARDUINO_C, "Arduino C++"), (Snippet.PYTHON, "Python"), (Snippet.OTHER, "Other"))

class SnippetForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(1, 64, 'Title should be no more than 64 characters')])
    language = SelectField("Language", coerce=int)
    body = TextAreaField("Content", validators=[DataRequired()])
    submit = SubmitField("Save", false_values="submit")
    cancel = SubmitField("Cancel", false_values="cancel")

    def __init__(self):
        super(SnippetForm, self).__init__()
        self.language.choices = choices

    def validate_language(self, field):
        if field.data == 0:
            raise ValidationError("You must select a language.")

class CommentForm(FlaskForm):
    body = TextAreaField("Content", validators=[DataRequired()])
    submit = SubmitField("Save", false_values="submit")
    cancel = SubmitField("Cancel", false_values="cancel")

class SearchForm(FlaskForm):
    search = StringField("Search Query", validators=[DataRequired()])
    submit = SubmitField("Search")