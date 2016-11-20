import datetime
import random
import string
import json

from app import db, app


def _random_string(length):
    return ''.join(random.choice(string.lowercase) for i in range(length))

class Configuration(db.Model):
    __tablename__ = 'config'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String, unique=True, nullable=False)
    private_key = db.Column(db.String, nullable=False, default=lambda :_random_string(20))
    model = db.Column(db.String, nullable=False)

class Timeline(db.Model):
    __tablename__ = 'timeline'
    id = db.Column(db.Integer, primary_key=True)
    config = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    value = db.Column(db.LargeBinary)

    def info(self):
        return {
            "timestamp": self.timestamp.isoformat()[:19]  + "Z",
            "data": json.loads(self.value)
        }

class KeyValue(db.Model):
    __tablename__ = 'keyvalue'
    id = db.Column(db.Integer, primary_key=True)
    config = db.Column(db.String, nullable=False)
    key = db.Column(db.String, nullable=False)
    value = db.Column(db.LargeBinary)


class Blob(db.Model):
    __tablename__ = 'blob'
    id = db.Column(db.Integer, primary_key=True)
    config = db.Column(db.String, nullable=False, unique=True)
    value = db.Column(db.LargeBinary)
