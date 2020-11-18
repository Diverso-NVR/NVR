import os

from flask import render_template, current_app
from flask_mail import Mail, Message

from premailer import transform


NVR_CLIENT_URL = os.environ.get("NVR_CLIENT_URL")
mail = Mail()


def send_async_email(app, msg: Message) -> None:
    """
    Sends message asynchronously
    """
    with app.app_context():
        mail.send(msg)


def send_email(subject: str, sender: str, recipients: list, html_body) -> None:
    """
    Creates message
    """
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.html = transform(html_body)
    send_async_email(current_app._get_current_object(), msg)


def send_verify_email(user, token_expiration: int) -> None:
    """
    Creates token, and email body
    """
    token = user.get_token(token_expiration, "verify_email")
    url = f"{NVR_CLIENT_URL}/api/verify-email/{token}"

    send_email(
        "[NVR] Подтверждение аккаунта",
        sender=current_app.config["ADMINS"][0],
        recipients=[user.email],
        html_body=render_template("email/verify_email.html", user=user, url=url),
    )


def send_reset_pass_email(user, token_expiration: int) -> None:
    """
    Creates token, and email body
    """
    token = user.get_token(token_expiration, "reset_pass")
    url = f"{NVR_CLIENT_URL}/reset-pass/{token}"

    send_email(
        "[NVR] Сброс пароля",
        sender=current_app.config["ADMINS"][0],
        recipients=[user.email],
        html_body=render_template("email/reset_pass.html", user=user, url=url),
    )


def send_access_request_email(admins: list, user) -> None:
    send_email(
        "[NVR] Запрос на доступ",
        sender=current_app.config["ADMINS"][0],
        recipients=admins,
        html_body=render_template(
            "email/access_request.html", user=user, url=NVR_CLIENT_URL
        ),
    )
