from flask import render_template, flash
from flask_mail import Message
from . import mail

def send_email(recipient, subject, template, **kwargs):
    msg = Message('[CodeMaker Buddy] ' + subject,
                  sender="codemakerbuddy@gmail.com", recipients=[recipient])
    msg.body = render_template('mail/' + template + '.txt', **kwargs)
    msg.html = render_template('mail/' + template + '.html', **kwargs)
    try:
        mail.send(msg)
    except:
        flash("Sorry but we could not send the email.", 'warning')