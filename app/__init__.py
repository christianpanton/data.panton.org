from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from raven.contrib.flask import Sentry

app = Flask(__name__)
app.config.from_object('config')

if app.config["SENTRY_DSN"]:
    Sentry(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app.commands import *

manager = Manager(app)
manager.add_command('db', MigrateCommand)
manager.add_command('initdb', InitDBCommand())
manager.add_command('create', CreateCommand())
manager.add_command('list', ListCommand())
manager.add_command('schema', SchemaCommand())

from app import views
from app import models

@manager.shell
def make_shell_context():
    return dict(app=app, db=db, models=models)
    