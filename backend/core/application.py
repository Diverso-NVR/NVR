"""
- creates a Flask app instance and registers the database object
"""
from gevent import monkey

monkey.patch_all()

from flask import Flask, request, g
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os

from core.models import Session

NVR_CLIENT_URL = os.environ.get('NVR_CLIENT_URL')
REDIS_HOST = os.environ.get('REDIS_HOST', '127.0.0.1')


def create_app(app_name="NVR_API"):
    """
    Creates flask_app instance
    """
    app = Flask(app_name)
    app.config.from_object('core.config.BaseConfig')


    limiter = Limiter(
        app,
        key_func=get_remote_address,
        default_limits=["100/minute", "10/second"]
    )

    @limiter.request_filter
    def header_whitelist():
        return request.headers.get("X-Goog-Resource-Uri") is not None


    from core.models import Session

    @app.before_request
    def before_request():
        g.session = Session()

    @app.teardown_request
    def teardown_request(exception):
        try:
            g.session.close()
        except:
            pass


    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


    from core.routes.merger import api as merger_api
    app.register_blueprint(merger_api, url_prefix="/api")

    from core.routes.google import api as google_api
    app.register_blueprint(google_api, url_prefix="/api")

    from core.routes.auth import api as auth_api
    app.register_blueprint(auth_api, url_prefix="/api")

    from core.routes.rooms import api as rooms_api
    app.register_blueprint(rooms_api, url_prefix="/api")

    from core.routes.sources import api as sources_api
    app.register_blueprint(sources_api, url_prefix="/api")

    from core.routes.users import api as users_api
    app.register_blueprint(users_api, url_prefix="/api")
    

    from core.models import User
    session = Session()
    if session.query(User).all() == []:
        user = User(email='admin@admin.com', password='nvr_admin')
        user.access = True
        user.email_verified = True
        user.role = 'admin'

        session.add(user)
        session.commit()
    session.close()


    from core.email import mail
    mail.init_app(app)


    from core.socketio import NvrNamespace
    socketio = SocketIO(app,
                        message_queue='redis://' + REDIS_HOST,
                        cors_allowed_origins=NVR_CLIENT_URL,
                        async_mode='gevent',
                        # logger=True, engineio_logger=True
                        )
    socketio = SocketIO(app)
    socketio.on_namespace(NvrNamespace('/websocket'))

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
                toaddrs=app.config['ADMINS'],
                subject='NVR Failure',
                credentials=auth,
                secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/nvr.log',
                                           maxBytes=10240,
                                           backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)

        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('NVR started')

    return app, socketio
