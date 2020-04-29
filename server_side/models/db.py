# -*- coding: utf-8 -*-
# !/usr/bin/python3.7


import pymysql


def get_db_con():
    '''
    db function
    :return: database connection object
    '''
    dbconnect = pymysql.connect(
        host='120.77.168.57',
        port=3306,
        user='dst_api',
        password='WDarmDW0a6uRFG3O',
        db='dst_api',
        charset='utf8'
    )  # 默认返回元组对象。
    return dbconnect


def get_db():
    '''
    a database cursor which return a tuple.
    :return:tuple cursor
    '''
    con = get_db_con()
    db = con.cursor()
    return db


def get_db_dict():
    '''
    a db cursor which return a dict
    :return:dict cursor
    '''
    con = get_db_con()
    dbd = con.cursor(cursor=pymysql.cursors.DictCursor)
    return dbd


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
        db.close()


