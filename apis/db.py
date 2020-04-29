# -*- coding: utf-8 -*-
# !/usr/bin/python3.7


import click
import pymysql
from flask import current_app, g
from flask.cli import with_appcontext


def get_db_con():
    '''
    db function
    :return: database connection object
    '''
    dbconnect = pymysql.connect(
        host=current_app.config['DB_HOST'],
        port=current_app.config['DB_PORT'],
        user=current_app.config['DB_USER'],
        password=current_app.config['DB_PASSWORD'],
        db=current_app.config['DB_DB'],
        charset=current_app.config['DB_CHARSET']
    )  # 默认返回元组对象。
    return dbconnect


def get_db():
    '''
    a database cursor which return a tuple.
    :return:tuple cursor
    '''
    if 'db' not in g:
        con = get_db_con()
        g.db = con.cursor()
    return g.db


def get_db_dict():
    '''
    a db cursor which return a dict
    :return:dict cursor
    '''
    if 'dbd' not in g:
        con = get_db_con()
        g.dbd = con.cursor(cursor=pymysql.cursors.DictCursor)
    return g.dbd


def commit_sql(sql, val):
    '''
    commit data to database based on the sql command
    :param sql: sql line
    :param val: pymysql format val
    :return: None
    '''
    db = get_db_con()
    with db.cursor() as cr:
        cr.execute(sql, val)
        db.commit()


def execute_sql_file(sql):
    '''
    :param sql: sql must be string and be a name of sql file.
    :return: None
    '''
    db = get_db()
    with current_app.open_resource(sql) as f:
        sqls = [sql.strip() for sql in f.read().decode('utf-8').split(';') if not None]
        for i in sqls:
            if i:
                db.execute(i)


def close_db(e=None):
    '''
    clear g and close database
    :param e: None
    :return: None
    '''
    db = g.pop('db', None)

    if db is not None:
        db.close()


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    execute_sql_file('schema.sql')
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)