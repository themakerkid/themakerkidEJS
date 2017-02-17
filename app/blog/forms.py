from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, ValidationError
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
            return True
        else:
            return False