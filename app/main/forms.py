# main/forms.py - form class for the search
# By Benjamin Murray

# Import the Base Form class to get methods like form.validate_on_submit()
from flask_wtf import FlaskForm

# Import Fields for the form
from wtforms import StringField, SubmitField, TextAreaField

# Import the DataRequired validator to check if the is something in a field
from wtforms.validators import DataRequired, Length, Email

# Overall Search Form
class SearchForm(FlaskForm):
    # Search box
    search = StringField("Search Query", validators=[DataRequired()])

    # Submit button
    submit = SubmitField("Search", false_values="search")

    # Cancel button
    cancel = SubmitField("Cancel", false_values="cancel")

# Contact Me
class ContactForm(FlaskForm):
    # Name
    name = StringField("Your name", validators=[DataRequired()])

    # Email
    email = StringField("Your email", validators=[DataRequired(), Length(1, 64, "Email is too long."), Email()])

    # Subject
    subject = StringField("Subject", validators=[DataRequired(), Length(1, 64, "Subject is too long.")])

    # Comment
    comment = TextAreaField("Your comment", validators=[DataRequired()])

    # Submit button
    submit = SubmitField("Send via email")