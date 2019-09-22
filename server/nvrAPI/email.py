from flask_mail import Mail, Message
from threading import Thread
from flask import render_template, current_app
import os

mail = Mail()


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email,
           args=(current_app._get_current_object(), msg)).start()


def send_verify_email(user, token_expiration):
    token = user.get_verify_token(token_expiration)
    send_email('[NVR] Подтверждение аккаунта',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/verify_template.txt',
                                         user=user, token=token),
               html_body=render_template('email/verify_template.html',
                                         user=user, token=token)
               )
