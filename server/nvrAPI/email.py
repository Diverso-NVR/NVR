from flask_mail import Mail, Message
from threading import Thread
from flask import render_template, current_app
import os

mail = Mail()

# export MAIL_SERVER=smtp.googlemail.com
# export MAIL_PORT=587
# export MAIL_USE_TLS=1
# export MAIL_USERNAME=<your-gmail-username>
# export MAIL_PASSWORD=<your-gmail-password>


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)


def send_verify_email(user):
    token = user.get_verify_token()
    send_email('[NVR] Подтверждение аккаунта',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/verify_template.txt',
                                         user=user, token=token),
               html_body=render_template('email/verify_template.html',
                                         user=user, token=token)
               )
