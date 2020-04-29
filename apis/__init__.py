# -*- coding: utf-8 -*-
# !/usr/bin/python3.7


from flask import Flask
import os


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='1587530221.480847jxbi9d5c42p0gi9',
        DB_HOST='120.77.168.57',
        DB_PORT=3306,
        DB_USER='dst_api',
        DB_PASSWORD='WDarmDW0a6uRFG3O',
        DB_DB='dst_api',
        DB_CHARSET='utf8',
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        # silent: set to ``True`` if you want silent failure for missing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # if is test, load the test config
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    from . import model
    model.init_app(app)

    from . import api
    app.register_blueprint(api.bp)

    from . import auth
    app.register_blueprint(auth.bp)

    # set url '/' and its 'name'.
    app.add_url_rule('/', endpoint='index')

    return app

