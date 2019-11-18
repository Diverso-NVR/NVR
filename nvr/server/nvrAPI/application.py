"""
- creates a Flask app instance and registers the database object
"""
<<<<<<< HEAD
from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from gevent import monkey
monkey.patch_all()
=======
from gevent import monkey
monkey.patch_all()

import os
from logging.handlers import SMTPHandler, RotatingFileHandler
import logging
from flask_socketio import SocketIO
from flask_cors import CORS
from flask import Flask, request
>>>>>>> 66e4e9a35265b9c96b4c5a25b61d27da93fcec95


NVR_CLIENT_URL = os.environ.get('NVR_CLIENT_URL')


def create_app(app_name="NVR_API"):
    """
    Creates flask_app instance
    """
    app = Flask(app_name)
    app.config.from_object('nvrAPI.config.BaseConfig')

    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    from nvrAPI.api import api
    app.register_blueprint(api, url_prefix="/api")

    from nvrAPI.models import db
    db.init_app(app)

    from nvrAPI.email import mail
    mail.init_app(app)

    from nvrAPI.socketio import NvrNamespace
<<<<<<< HEAD
    socketio = SocketIO(app, message_queue='redis://',
                        cors_allowed_origins=NVR_CLIENT_URL, async_mode='gevent',
=======
    socketio = SocketIO(app,
                        message_queue='redis://',
                        cors_allowed_origins=NVR_CLIENT_URL,
                        async_mode='gevent',
>>>>>>> 66e4e9a35265b9c96b4c5a25b61d27da93fcec95
                        logger=True, engineio_logger=True
                        )
    socketio.on_namespace(NvrNamespace('/nvr-socket'))

    @socketio.on_error_default
    def default_error_handler(e):
        print(request.event["message"])
        print(request.event["args"])

    # logging
    if not app.debug:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] and app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'],
                        app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='NVR Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/nvr.log', maxBytes=10240,
                                           backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('NVR started')

    return app, socketio
