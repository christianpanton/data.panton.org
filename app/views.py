# -*- coding: utf-8 -*-

import json

import dateutil
import dateutil.parser
import sqlalchemy.orm.exc

from flask import request, abort, jsonify, send_file, Response

from app import app, db
from app.models import *


@app.route('/<slug>', methods=["GET", "POST"])
def main(slug):

    try:
        c = Configuration.query.filter(Configuration.slug == slug).one()
    except sqlalchemy.orm.exc.NoResultFound:
        abort(404)

    if request.method == "GET":

        if c.model == "keyvalue":
            kv = KeyValue.query.filter(KeyValue.config == slug).all()
            val = {}
            for el in kv:
                val[el.key] = json.loads(el.value)

        elif c.model == "timeline":
            tl = Timeline.query.filter(Timeline.config == slug).order_by(Timeline.timestamp).all()
            val = map(lambda el: el.info(), tl)

        elif c.model == "blob":
            try:
                b = Blob.query.filter(Blob.config == slug).one()
            except sqlalchemy.orm.exc.NoResultFound:
                return ('', 204)

            return b.value

        else:
            raise NotImplementedError

        return jsonify(val)

    else: # update

        if request.headers.get('X-Auth') != c.private_key:
            abort(403)

        if c.model not in ["timeline", "blob"]:
            abort(404)
        
        if c.model == "timeline":
            
            tl = Timeline()
            tl.config = c.slug
            tl.value = json.dumps(request.get_json(force=True))

            if request.headers.get('X-Timestamp'):
                t = dateutil.parser.parse(request.headers.get('X-Timestamp'))
                if t.tzinfo == None:
                    t = t.replace(tzinfo=dateutil.tz.tzutc())
                t = t.astimezone(dateutil.tz.tzutc())
                tl.timestamp = t

            db.session.add(tl)
            db.session.commit()

            return ('', 204)

        elif c.model == "blob":
            
            try:
                b = Blob.query.filter(Blob.config == slug).one()
            except sqlalchemy.orm.exc.NoResultFound:
                b = Blob()
                b.config = c.slug
                db.session.add(b)

            b.value = request.get_data()
            db.session.commit()

            return ('', 204)





@app.route('/<slug>/<key>', methods=["GET", "POST"])
def key(slug, key):

    try:
        c = Configuration.query.filter(Configuration.slug == slug).one()
    except sqlalchemy.orm.exc.NoResultFound:
        abort(404)

    if c.model not in ["keyvalue"]:
        abort(404)

    if request.method == "GET":

        try:
            kv = KeyValue.query.filter(KeyValue.config == slug, KeyValue.key == key).one()
        except sqlalchemy.orm.exc.NoResultFound:
            abort(404)

        val = json.loads(kv.value)

        return jsonify(val)

    else:

        if request.headers.get('X-Auth') != c.private_key:
            abort(403)

        if c.model == "keyvalue":

            try:
                kv = KeyValue.query.filter(KeyValue.config == slug, KeyValue.key == key).one()
            except sqlalchemy.orm.exc.NoResultFound:
                kv = KeyValue()
                kv.config = c.slug
                kv.key = key
                db.session.add(kv)

            kv.value = json.dumps(request.get_json(force=True))
            db.session.commit()

            return ('', 204)