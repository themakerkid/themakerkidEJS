from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, ValidationError
from wtforms.validators import Length, Required, Regexp, Email, EqualTo, Optional
from ..models import User, db

class LoginForm(FlaskForm):
    user_or_email = StringField('Username or Email', validators=[Required(), Length(1, 64,
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
    title = StringField("Title", validators=[Required(), Length(1, 64, message="Title should be no more than 64 characters.")])
    body = TextAreaField("Content", validators=[Required()])
    #tags = StringField("Tags (Please seperate with commas with no spaces in between them)", validators=[Required()])
    submit = SubmitField("Submit")
    cancel = SubmitField("Cancel", false_values="cancel")

class CommentForm(FlaskForm):
    body = TextAreaField("Content", validators=[Required()])
    submit = SubmitField("Save", false_values="submit")
    cancel = SubmitField("Cancel", false_values="cancel")

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[Required(), Length(1, 64), Regexp('^[a-zA-Z._][a-zA-Z0-9._]*$', 0,
                                                                      'Your username can only contain letters, numbers, dots, underscores '
                                                                      'and cannot start with a number.')])
    email = StringField('Your parents email', validators=[Required(), Email(), Length(1, 64)])
    password = PasswordField('Password', validators=[Required(), EqualTo('com_password', message="The two passwords don't match.")])
    com_password = PasswordField('Confirm Password', validators=[Required()])
    check_email = BooleanField("I agree that I have used my parent's email if I am 12 or under", validators=[Required()], default=True)
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