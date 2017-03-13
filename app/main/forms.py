# main/forms.py - form class for the search
# By Benjamin Murray

# Import the Base Form class to get methods like form.validate_on_submit()
from flask_wtf import FlaskForm

# Import Fields for the form
from wtforms import StringField, SubmitField

# Import the DataRequired validator to check if the is something in a field
from wtforms.validators import DataRequired

# Overall Search Form
class SearchForm(FlaskForm):
    # Search box
    search = StringField("Search Query", validators=[DataRequired()])

    # Submit button
    submit = SubmitField("Search", false_values="search")

    # Cancel button
    cancel = SubmitField("Cancel", false_values="cancel")