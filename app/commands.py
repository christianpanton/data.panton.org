from flask_script import Command, Manager, Option

from app.models import *
from app import db, app, models

class InitDBCommand(Command):
    "inititalize database"

    def run(self):
        db.drop_all()
        db.create_all()

class CreateCommand(Command):
    "create a new dataset"

    option_list = (
        Option('--name', '-n', dest='slug'),
        Option('--type', '-t', dest='model'),
    )

    def run(self, slug, model):

        if model is None:
            print "type required"
            return

        if slug is None:
            print "name required"
            return

        if model not in ["timeline", "keyvalue", "blob"]:
            print "invalid type", model
            return

        c = models.Configuration()
        c.slug = slug
        c.model = model
        db.session.add(c)
        db.session.commit()

        print c.model, c.slug, c.private_key

class ListCommand(Command):
    "print list of all datasets"

    def run(self):
        for c in models.Configuration.query.all():
            print c.model, c.slug, c.private_key

class SchemaCommand(Command):
    "print schema for a table"

    option_list = (
        Option('--model', '-m', dest='model'),
    )

    def run(self, model):
        from sqlalchemy.schema import CreateTable
        try:
            t = getattr(models, model) 
            print CreateTable(t.__table__).compile(db.engine)
        except AttributeError:
            print "no such table", model