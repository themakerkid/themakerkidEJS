from flask import request, Markup, current_app
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin, AnonymousUserMixin
from markdown import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.extra import ExtraExtension
from . import db, login
import hashlib

hilite = CodeHiliteExtension(linenums=True, css_class='highlight')
extras = ExtraExtension()

post_tags = db.Table("post_tags",
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id')),
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'))
)

project_parts = db.Table("project_parts",
    db.Column('project_id', db.Integer, db.ForeignKey('projects.id')),
    db.Column('part_id', db.Integer, db.ForeignKey('parts.id'))
)

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    parents_email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    avatar_hash = db.Column(db.String(32))
    about_me = db.Column(db.Text)
    date_registered = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    posts = db.relationship('Post', backref="author", lazy="dynamic")
    comments = db.relationship('Comment', backref="author", lazy="dynamic")
    snippets = db.relationship('Snippet', backref="author", lazy="dynamic")
    snippet_comments = db.relationship('SnippetComment', backref="author", lazy="dynamic")
    projects = db.relationship('Project', backref="author", lazy="dynamic")
    project_comments = db.relationship('ProjectComment', backref="author", lazy="dynamic")

    projects_liked = []

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.parents_email != None and self.avatar_hash == None:
            self.avatar_hash = hashlib.md5(self.parents_email.encode("utf-8")).hexdigest()

    @property
    def password(self):
        raise AttributeError("You cannot read the password!")
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def chk_psswd(self, password):
        return check_password_hash(self.password_hash, password)

    def setLastSeen(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
    
    def getAvatar(self, size=100, default='monsterid', rating='g'):
        if request.is_secure:
            base_url = 'https://secure.gravatar.com/avatar'
        else:
            base_url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(self.parents_email.encode('utf-8')).hexdigest()
        full_url = "%s/%s?s=%i&d=%s&?r=%s" % (base_url, hash, size, default, rating)
        return full_url
    
    def generateResetToken(self, expiration=3600):
        serializer = Serializer(current_app.config["SECRET_KEY"], expiration)
        return serializer.dumps({'reset': self.id, 'email': self.parents_email})

    @staticmethod
    def resetPassword(password, token):
        serializer = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = serializer.loads(token)
        except:
            return False
        user = User.query.filter_by(parents_email=data["email"]).first()
        if not user:
            return False
        if data["reset"] != user.id:
            return False
        user.password = password
        db.session.add(user)
        return True

    def generateConfirmationToken(self, expiration=3600):
        serializer = Serializer(current_app.config["SECRET_KEY"], expiration)
        return serializer.dumps({'confirm_id': self.id})
    
    def confirmAccount(self, token):
        serializer = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = serializer.loads(token)
        except:
            return False
        if data["confirm_id"] != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def admin(self):
        return self.username == "Benjamin"

    def __repr__(self):
        return 'User <%s>' % self.username

class AnonymousUser(AnonymousUserMixin):
    id = 0

    def admin(self):
        return False

login.anonymous_user = AnonymousUser

class Post(db.Model):
    __tablename__ = 'posts'
    __searchable__ = ['title', 'body']

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    body = db.Column(db.Text)
    summary = db.Column(db.Text)
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    date_posted = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    published = db.Column(db.Boolean, default=True)
    title = db.Column(db.String(64))
    tags = db.relationship('Tag', secondary=post_tags,
                           backref=db.backref('posts', lazy='dynamic'))

    #@staticmethod
    #def body_changed(target, value, oldvalue, initiator):
    #    target.body_html = markdown(value, output_format='html')

#db.event.listen(Post.body, 'set', Post.body_changed)

    @property
    def body_html(self):
        markdown_content = markdown(self.body, extensions=[hilite, extras])
        return markdown_content
    
    @property
    def summary_html(self):
        markdown_content = markdown(self.summary, extensions=[hilite, extras])
        return markdown_content

    def changedBody(self):
        new_summary = self.body
        new_summary = new_summary.split(' ')
        new_summary = new_summary[:80]
        new_summary = ' '.join(new_summary)
        if not new_summary == self.body:
            new_summary += '...'
        self.summary = new_summary

    def __repr__(self):
        return "Post <%s>" % self.title

class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))

    def __repr__(self):
        return 'Tag <%s>' % self.name

def addTag(name):
    tag = Tag(name=name)
    db.session.add(tag)
    db.session.commit()
    print Tag.query.all()

def addTags(tags_name):
    for i in range(len(tags_name)):
        tag = Tag(name=tags_name[i])
        db.session.add(tag)
    db.session.commit()
    print Tag.query.all()

class Comment(db.Model):
    __tablename__ = 'comments'
    __searchable__ = ['body']

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    body = db.Column(db.Text)
    #body_html = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    #@staticmethod
    #def body_changed(target, value, oldvalue, initiator):
    #    target.body_html = markdown(value, output_format='html')

#db.event.listen(Comment.body, 'set', Comment.body_changed)

    @property
    def body_html(self):
        hilite = CodeHiliteExtension(linenums=True, css_class='highlight')
        extras = ExtraExtension()
        markdown_content = markdown(self.body, extensions=[hilite, extras])
        return Markup(markdown_content)

class Snippet(db.Model):
    HTML = 1
    CSS = 2
    JAVASCRIPT = 3
    ARDUINO_C = 4
    PYTHON = 5
    PROCESSING = 6
    SQL = 7
    OTHER = 8

    __tablename__ = 'snippets'
    __searchable__ = ['title', 'body']
    
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    body = db.Column(db.Text)
    summary = db.Column(db.Text)
    #body_html = db.Column(db.Text)
    code_type_id = db.Column(db.SmallInteger)
    comments = db.relationship('SnippetComment', backref='snippet', lazy='dynamic')
    date_posted = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    title = db.Column(db.String(64))

    #@staticmethod
    #def body_changed(target, value, oldvalue, initiator):
    #    target.body_html = markdown(value, output_format='html')

    @property
    def body_html(self):
        markdown_content = markdown(self.body, extensions=[hilite, extras])
        return markdown_content

    @property
    def summary_html(self):
        markdown_content = markdown(self.summary, extensions=[hilite, extras])
        return markdown_content

    def changedBody(self):
        new_summary = self.body
        new_summary = new_summary.split(' ')
        new_summary = new_summary[:80]
        new_summary = ' '.join(new_summary)
        if not new_summary == self.body:
            new_summary += '...'
        self.summary = new_summary

class SnippetComment(db.Model):
    __tablename__ = 'snippet_comments'
    __searchable__ = ['body']
    
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    body = db.Column(db.Text)
    #body_html = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    snippet_id = db.Column(db.Integer, db.ForeignKey('snippets.id'))

    #@staticmethod
    #def body_changed(target, value, oldvalue, initiator):
    #    target.body_html = markdown(value, output_format='html')

#db.event.listen(Comment.body, 'set', Comment.body_changed)

    @property
    def body_html(self):
        markdown_content = markdown(self.body, extensions=[hilite, extras])
        return Markup(markdown_content)

class Project(db.Model):
    __tablename__ = 'projects'
    __searchable__ = ['title', 'description', 'vid_url', 'parts']

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    code = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    description = db.Column(db.Text)
    document_html = db.Column(db.Text)
    likes = db.Column(db.Integer)
    parts = db.Column(db.Text)
    status = db.Column(db.Boolean, default=True)
    steps = db.Column(db.Integer)
    title = db.Column(db.String(64))
    pdf_name = db.Column(db.String(64))
    vid_url = db.Column(db.String(64))
    comments = db.relationship('ProjectComment', backref='project', lazy="dynamic")
    #parts = db.relationship('Part', secondary=project_parts,
                            #backref=db.backref('projects', lazy='dynamic'))

    @property
    def description_html(self):
        markdown_content = markdown(self.description, extensions=[hilite, extras])
        return Markup(markdown_content)

    @property
    def steps_html(self):
        markdown_content = markdown(self.steps, extensions=[hilite, extras])
        return Markup(markdown_content)

    @property
    def code_html(self):
        markdown_content = markdown(self.code, extensions=[hilite, extras])
        return Markup(markdown_content)

class ProjectComment(db.Model):
    __tablename__ = 'project_comments'
    __searchable__ = ['body']

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    body = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))

    @property
    def body_html(self):
        markdown_content = markdown(self.body, extensions=[hilite, extras])
        return Markup(markdown_content)

class Part(db.Model):
    __tablename__ = 'parts'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))

    def __repr__(self):
        return "Part <%s>" % self.name

@login.user_loader
def load_user(id):
    return User.query.get(int(id))