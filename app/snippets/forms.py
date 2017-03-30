from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, ValidationError
from wtforms.validators import Length, DataRequired
from ..models import Snippet

choices = ((0, "Please select a language"), (Snippet.HTML, "HTML"), (Snippet.CSS, "CSS"), (Snippet.JAVASCRIPT, "JavaScript"), (Snippet.ARDUINO_C, "Arduino C++"), (Snippet.PYTHON, "Python"), (Snippet.PROCESSING, "Processing.js"),(Snippet.SQL, "SQL"), (Snippet.OTHER, "Other"))

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
    search = StringField("Search Query")
    language = SelectField("Language", choices=choices, coerce=int)
    submit = SubmitField("Search")

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        self.search_query = False
        self.language_used = False
        self.both = False
    
    def validate_language(self, field):
        if field.data is not None:
            self.language_used = True

    def validate_search(self, field):
        if field.data is not None:
            if self.language_used:
                self.both, self.language_used = True, True
            else:
                self.language_used = True
        elif (not self.language_used) and (field.data is None):
            raise ValidationError("You must choose either a language or type in a search query.")
        else:
            raise ValidationError("Error!")