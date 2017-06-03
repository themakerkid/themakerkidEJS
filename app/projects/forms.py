from flask_wtf import FlaskForm
from wtforms import StringField, SelectMultipleField, TextAreaField, IntegerField, RadioField, SubmitField
from wtforms.fields.html5 import URLField
from wtforms.validators import DataRequired, Length, Optional
from ..models import Part

class ProjectForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(1, 64, "Title must be under 64 characters")])
    description = TextAreaField("Description (with images)", validators=[DataRequired()])
    vid_url = URLField("Video URL (optional)", validators=[Optional(), Length(1, 100, "Video URL must be less than 100 characters")])
    parts = TextAreaField("Parts (Each on a new line)")
    steps = TextAreaField("Steps [Leave 3 stars/asterisks (***) between each step]", validators=[DataRequired()])
    code = TextAreaField("The code!", validators=[DataRequired()])
    status = RadioField("", coerce=int, choices=[(0, "Draft"), (1, "Final")], default="0")
    submit = SubmitField("Save")

class CommentForm(FlaskForm):
    body = TextAreaField("Content", validators=[DataRequired()])
    submit = SubmitField("Save")