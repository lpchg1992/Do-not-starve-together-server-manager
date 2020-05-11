# -*- coding: utf-8 -*-
# !/usr/bin/python3.7


import functools


from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from apis.db import commit_sql, get_db_dict
from apis.model import SocketFunc


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        inviteCode = str(request.form['invitecode'])
        kuCode = request.form['kucode']
        steamNickNname = request.form['steamnickname']
        db = get_db_dict()
        db.execute(
            'SELECT id FROM user WHERE username = %s', (username,)
        )
        username_result = db.fetchone()
        db.execute(
            'SELECT code, used FROM invite_code WHERE code = %s', (inviteCode,)
        )
        inviteCode_result = db.fetchone()

        error = None

        if not username:
            error = 'Username is required'
        elif not password:
            error = 'Password is required'
        elif not inviteCode:
            error = 'inviteCode is required'
        elif username_result is not None:
            error = 'User {} is already registered.'.format(username)
        elif inviteCode_result['code'] != inviteCode or inviteCode_result['used']:
            error = 'invalid code.'
        if error is None:
            lv_ = inviteCode.split('+')
            lv = lv_[-1]
            commit_sql('INSERT INTO user (username, password, level, kucode, steamnickname) VALUES (%s,%s,%s,%s,%s)',
                       (username, generate_password_hash(password), lv, kuCode, steamNickNname,))
            commit_sql('UPDATE invite_code SET used_by = %s, used = %s WHERE code = %s', (username, 1, inviteCode))
            error = 'Success!'
        flash(error)

    return redirect(url_for('index'))


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db_dict()
        error = None
        db.execute('SELECT * FROM user WHERE username = %s', (username,))
        user = db.fetchone()
        if user is None:
            error = 'No such user or incorrect password'
        elif not check_password_hash(user['password'], password):
            error = 'No such user or incorrect password'
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            error = 'Login Success!'
            flash(error)
            return redirect(url_for('api.manager_index'))
        else:
            flash(error)
            return redirect(url_for('index'))


# this function will invoke evry time before the view function run
# if the user login, there will be a user data stored in g.
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        get_db_dict().execute(
            'SELECT * FROM user WHERE id = %s', (user_id,)
        )
        g.user = get_db_dict().fetchone()
        serversa = SocketFunc(cmd='smng@server_infos:dsls@10').client_side()
        serversr = SocketFunc(cmd='smng@server_infos:dslsr@10').client_side()

        g.dsl = {'running': len(serversr.split('@'))-1, 'all': len(serversa.split('@'))-1}
        g.dsls = []
        for i in serversa.split('@'):
            if i:
                g.dsls.append({'id': i.split(' ')[0], 'statu': i.split(' ')[1], 'name': i.split(' ')[2]})


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# a decorator to require login before
# view attr is required for recieve a func
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return render_template('index.html')
        return view(**kwargs)
    return wrapped_view

