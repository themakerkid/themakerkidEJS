from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import Length, Required
from ..models import User, db

class LoginForm(FlaskForm):
    user_or_email = StringField('Username or Email', validators=[Required(), Length(max=64,
                    message="Your username or email is too long.")])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Submit")

    def validate_credentials(self, username_field, psswd_field):
        user = User.query.filter(db.or_(User.username==username_field.data, User.parents_email==username_field.data)).first()
        if not user == None and user.chk_psswd(psswd_field.data):
            return user
        else:
            return False

class PostForm(FlaskForm):
    title = StringField("Title", validators=[Required(), Length(max=64, message="Title should be no more than 64 characters.")])
    body = TextAreaField("Content", validators=[Required()])
    #tags = StringField("Tags (Please seperate with commas with no spaces in between them)", validators=[Required()])
    submit = SubmitField("Submit")

class CommentForm(FlaskForm):
    body = TextAreaField("Content", validators=[Required()])
    submit = SubmitField("Save")