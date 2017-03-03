from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, ValidationError
from wtforms.validators import Length, DataRequired, Regexp, Email, EqualTo, Optional, StopValidation
from ..models import User, db

class LoginForm(FlaskForm):
    user_or_email = StringField('Username or Email', validators=[DataRequired(), Length(1, 64,
                    message="Your username or email is too long.")])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Submit")
    cancel = SubmitField("Cancel")

    def validate_credentials(self, username_field, psswd_field):
        user = User.query.filter(db.or_(User.username==username_field.data, User.parents_email==username_field.data)).first()
        if not user == None and user.chk_psswd(psswd_field.data):
            return user
        else:
            return False

class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(1, 64, message="Title should be no more than 64 characters.")])
    body = TextAreaField("Content", validators=[DataRequired()])
    #tags = StringField("Tags (Please seperate with commas with no spaces in between them)", validators=[DataRequired()])
    submit = SubmitField("Submit")
    cancel = SubmitField("Cancel", false_values="cancel")

class CommentForm(FlaskForm):
    body = TextAreaField("Content", validators=[DataRequired()])
    submit = SubmitField("Save", false_values="submit")
    cancel = SubmitField("Cancel", false_values="cancel")

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 64), Regexp('^[a-zA-Z._][a-zA-Z0-9._]*$', 0,
                                                                      'Your username can only contain letters, numbers, dots, underscores '
                                                                      'and cannot start with a number.')])
    email = StringField('Your parents email', validators=[DataRequired(), Email(), Length(1, 64)])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('com_password', message="The two passwords don't match.")])
    com_password = PasswordField('Confirm Password', validators=[DataRequired()])
    check_email = BooleanField("I agree that I have used my parent's email if I am 12 or under", validators=[DataRequired("Please confirm that you have used your parent's email")])
    submit = SubmitField("Register", false_values="submit")
    cancel = SubmitField("Cancel", false_values="cancel")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("Username already exists")
    
    def validate_email(self, field):
        if User.query.filter_by(parents_email=field.data).first():
            raise ValidationError("Email already exists")

class EditProfile(FlaskForm):
    about_me = TextAreaField("About Me")
    submit = SubmitField("Save", false_values="submit")
    cancel = SubmitField("Cancel", false_values="cancel")

class ResetPasswordRequest(FlaskForm):
    parents_email = StringField("Your parent's email", validators=[DataRequired(), Email()])
    submit = SubmitField("Submit", false_values="submit")
    cancel = SubmitField("Cancel", false_values="cancel")
    
class ResetPassword(FlaskForm):
    password = PasswordField("New Password", validators=[DataRequired(), EqualTo("com_password", "The passwords don't match.")])
    com_password = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Submit", false_values="submit")
    cancel = SubmitField("Cancel", false_values="cancel")

class SearchForm(FlaskForm):
    search = StringField("Search Query", validators=[DataRequired()])
    submit = SubmitField("Search")