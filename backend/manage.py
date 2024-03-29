"""
- provides a command line utility for interacting with the
  application to perform interactive debugging and setup
"""

from flask import Flask
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy

from core.models import Room, Source, Record

app = Flask(__name__)
app.config.from_object("core.config.BaseConfig")

db = SQLAlchemy()
db.init_app(app)

migrate = Migrate(app, db)
manager = Manager(app)

# provide a migration utility command
manager.add_command("db", MigrateCommand)


# enable python shell with application context
@manager.shell
def shell_ctx():
    return dict(
        app=app,
        db=db,
        Room=Room,
        Source=Source,
        Record=Record,
    )


if __name__ == "__main__":
    manager.run()
