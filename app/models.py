from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from markdown import markdown
from . import db, login

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    parents_email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    date_registered = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    posts = db.relationship('Post', backref="author", lazy="dynamic")

    @property
    def password(self):
        raise AttributeError("You cannot read the password!")
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def chk_psswd(self, password):
        return check_password_hash(self.password_hash, password)

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    title = db.Column(db.String(64))

    @staticmethod
    def body_changed(target, value, oldvalue, initiator):
        target.body_html = markdown(value, output_format='html')

db.event.listen(Post.body, 'set', Post.body_changed)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))