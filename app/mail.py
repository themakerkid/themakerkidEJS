from flask import render_template, flash
from flask_mail import Message
from . import mail

def send_email(recipient, subject, template, **kwargs):
    msg = Message('[The MAKER Kid] ' + subject,
                  sender="themakerkid@gmail.com", recipients=[recipient])
    msg.body = render_template('mail/' + template + '.txt', **kwargs)
    msg.html = render_template('mail/' + template + '.html', **kwargs)
    try:
        mail.send(msg)
    except:
        flash("Sorry but we could not send you the email.", 'warning')