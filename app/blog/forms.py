# blog/forms.py - All the form classes for the Blog
# By Benjamin

# For redirecting to last url
from flask import redirect, session, url_for

# Import the base form class and recaptcha
from flask_wtf import FlaskForm, RecaptchaField, Recaptcha

# Import all the necessary fields such as a textarea (TextAreaField()).
from wtforms import BooleanField, PasswordField, SelectMultipleField, StringField, SubmitField, TextAreaField, RadioField, ValidationError

# Import all the validators such as making sure that there is something inside of a field (DataRequired())
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp

# Import some models to check credentials and to loop through all the Tags (multiple select)
from ..models import Tag, User, db

# Login Form class
class LoginForm(FlaskForm):
    # Username or email
    user_or_email = StringField('Username or Email', validators=[Length(max=64,
                    message="Your username or email is too long.")])
    
    # Password
    password = PasswordField('Password')

    # Remember me
    remember_me = BooleanField("Remember Me")

    
    submit = SubmitField("Submit", false_values="submit")
    cancel = SubmitField("Cancel", false_values="cancel")

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate_user_or_email(self, field):
        # Import checkBtn function to check which button was pressed (at the top is too early to import)
        from views import checkBtn
        if checkBtn("submit", self, validation=False):
            user = User.query.filter(db.or_(User.username==field.data, User.parents_email==field.data)).first()
            if not user == None:
                self.user = user
            else:
                raise ValidationError("Invalid username or email.")
    
    def validate_password(self, field):
        if self.user != None and not self.user.chk_psswd(field.data):
            raise ValidationError("Invalid password.")

class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(1, 64, message="Title should be no more than 64 characters.")])
    body = TextAreaField("Content", validators=[DataRequired()])
    tags = SelectMultipleField("Tags (You can hold down Ctrl or Command to select more than one)", coerce=int)
    published = BooleanField("Do you want to make this public?")
    submit = SubmitField("Submit")
    cancel = SubmitField("Cancel", false_values="cancel")

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.tags.choices = [(tag.id, tag.name) for tag in Tag.query.order_by(Tag.name.asc()).all()]

class CommentForm(FlaskForm):
    body = TextAreaField("Content", validators=[DataRequired()])
    submit = SubmitField("Save", false_values="submit")
    cancel = SubmitField("Cancel", false_values="cancel")

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 64), Regexp('^[a-zA-Z._][a-zA-Z0-9._]*$', 0,
                                                                      'Your username can only contain letters, numbers, dots, underscores '
                                                                      'and cannot start with a number.')])
    email = StringField('Your parent/guardian\'s or your own email', validators=[DataRequired(), Email(), Length(1, 64)])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('com_password', message="The two passwords don't match.")])
    com_password = PasswordField('Confirm Password', validators=[DataRequired()])
    recaptcha = RecaptchaField("Recaptcha", validators=[Recaptcha("You must confirm the recaptcha.")])
    check_email = RadioField("This will not be visible to anyone", choices=[
                                                                        ('thirteen', 'I am thirteen or over so I can use my own email'), ('under_12', 'I am 12 or under and have used my parent/guardian\'s email')
                                                                    ], default="under_12", validators=[DataRequired()])
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

    def validate_parents_email(self, field):
        if not User.query.filter_by(parents_email=field.data).first():
            raise ValidationError("Email not registered with this website.")
    
class ResetPassword(FlaskForm):
    password = PasswordField("New Password", validators=[DataRequired(), EqualTo("com_password", "The passwords don't match.")])
    com_password = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Submit", false_values="submit")
    cancel = SubmitField("Cancel", false_values="cancel")

class SearchForm(FlaskForm):
    search = StringField("", validators=[DataRequired()])
    submit = SubmitField("Search")