# snippets/forms.py - All the forms for the snippet blueprint
# By Benjamin Murray

# Import base form class and recaptcha
from flask_wtf import FlaskForm, RecaptchaField, Recaptcha

# Import the form fields required by form class
from wtforms import StringField, SubmitField, SelectField, TextAreaField, ValidationError

# Import some of the validators
from wtforms.validators import Length, DataRequired

# Import Snippet model to get ids of languages
from ..models import Snippet

# Create choices variable to stop repetition
choices = ((0, "Please select a language"), (Snippet.ARDUINO_C, "Arduino C++"), (Snippet.HTML, "HTML"), (Snippet.CSS, "CSS"), (Snippet.JAVASCRIPT, "JavaScript"), (Snippet.PYTHON, "Python"), (Snippet.PROCESSING, "Processing.js"), (Snippet.SCRATCH, "Scratch"), (Snippet.SQL, "SQL"), (Snippet.OTHER, "Other"))

# Form to create/edit a snippet
class SnippetForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(1, 64, 'Title should be no more than 64 characters')])
    language = SelectField("Language", coerce=int)
    body = TextAreaField("Content", validators=[DataRequired()])
    submit = SubmitField("Save", false_values="submit")
    cancel = SubmitField("Cancel", false_values="cancel")

    def __init__(self, *args, **kwargs):
        super(SnippetForm, self).__init__(*args, **kwargs)
        self.language.choices = choices

    def validate_language(self, field):
        # Custom validation
        if field.data == 0:
            raise ValidationError("You must select a language.")

# Form to create/edit a snippet
class CommentForm(FlaskForm):
    body = TextAreaField("Content", validators=[DataRequired()])
    submit = SubmitField("Save", false_values="submit")
    cancel = SubmitField("Cancel", false_values="cancel")

# Snippet search form
class SearchForm(FlaskForm):
    search = StringField("Search Query")
    language = SelectField("Language", choices=choices, coerce=int)
    submit = SubmitField("Search")

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)

        # State which field has been used
        self.search_query = False
        self.language_used = False
        self.both = False
    
    def validate_language(self, field):
        if field.data:
            # If language select field has been used:
            self.language_used = True

    def validate_search(self, field):
        if field.data:
            if self.language_used:
                # Set both to be true
                self.both, self.search_query = True
            else:
                # Just state that the search box has been used
                self.search_query = True
        elif (not self.language_used) and (field.data):
            # If no search has been provided, raise an error
            raise ValidationError("You must choose either a language or type in a search query.")