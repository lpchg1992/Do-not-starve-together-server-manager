# -*- coding: utf-8 -*-
# !/usr/bin/python3.7
import docker
import os
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort

from werkzeug.security import check_password_hash, generate_password_hash

from apis.auth import login_required

from apis.model import SocketFunc

from apis.db import commit_sql, get_db_dict

bp = Blueprint('api', __name__)


@bp.route('/', methods=('GET', 'POST'))
def index():
    if g.user:
        return redirect(url_for('api.manager_index'))
    else:
        return render_template('index.html')


@bp.route('/manager_index')
@login_required
def manager_index():
    userlevel_ = int(g.user['level'])

    return render_template('manager_index.html', userlevel=userlevel_)


@bp.route('/start_dst_server/<gid>')
@login_required
def start_dst_server(gid):
    if int(g.user['level']) >= 1:
        info = SocketFunc(cmd=f'server start@{gid}').client_side()
    else:
        info = 'Sorry, Do not have the Authority!'
    flash(info)
    return redirect(url_for('api.manager_index'))


@bp.route('/stop_dst_server/<gid>')
@login_required
def stop_dst_server(gid):
    if int(g.user['level']) >= 1:
        info = SocketFunc(cmd=f'server stop@{gid}').client_side()
    else:
        info = 'Sorry, Do not have the Authority!'
    flash(info)
    return redirect(url_for('api.manager_index'))


@bp.route('/server_manager/<gid>/<gname>')
@login_required
def server_manager(gid, gname):
    return render_template('server_manager.html', name=gname, id=gid, userlevel=int(g.user['level']))


@bp.route('/game_user_auth_list/<cls_>/<gname>/<gid>')
@login_required
def game_user_auth_list(cls_, gname, gid):
    cls = cls_
    cls___ = None
    if cls == 'adminlist':
        cls___ = '管理员名单'
    elif cls == 'whitelist':
        cls___ = '白名单'
    elif cls == 'blocklist':
        cls___ = '黑名单'

    listNow = []

    recentPlayer = []

    if request.method == 'POST':
        text = request.form['text']
        info = None
        if not text and not cls:
            error = 'Content Should not be empty!'
            flash(error)
        else:
            info = 'Please wait...'
            flash(info)
            cmdS = f"guid@{cls}:{text}@{g.user['level']}@{gname}"
            info = SocketFunc(cmd=cmdS).client_side()
        if info:
            flash(info)
    return render_template('game_user_auth_list.html', name=gname, cls__=cls___, userlevel=g.user['level'])


@bp.route('/mod_manager', methods=('GET', 'POST'))
@login_required
def mod_manager():
    db = get_db_dict()
    db.execute('SELECT * FROM mods')
    mods_ = db.fetchall()
    info = None
    if request.method == 'POST':
        modName = request.form['modname']
        modUrl = request.form['modurl']
        cmd = f'{modName}&&{modUrl}'
        cmd__ = f"modm@add_mod_to_db^{cmd}@{g.user['level']}"
        info = SocketFunc(cmd=cmd__).client_side()

        if info:
            flash(info)
        return redirect(url_for('api.mod_manager'))
    if info:
        flash(info)
    return render_template('mod_manager.html', mods=mods_, userlevel=g.user['level'])


@bp.route('/modm/<modid>/<int:delete>/<int:activate>/<int:ban>', methods=('GET', 'POST'))
@login_required
def modm(modid, delete, activate, ban):
    info = None
    if delete:
        cmd__ = f'modm@mod_db_remove^{modid}@{g.user["level"]}'
        info = SocketFunc(cmd=cmd__).client_side()
    if activate or ban:
        statue = None
        if activate:
            statue = '1'
        if ban:
            statue = '0'
        if statue:
            cmd__ = f'modm@mod_db_statue^{modid} {statue}@{g.user["level"]}'
            info = SocketFunc(cmd=cmd__).client_side()
    if info:
        flash(info)
    return redirect(url_for('api.mod_manager'))


@bp.route('/smng/<cmd_>')
@login_required
def smng(cmd_):
    cmds = cmd_.split(' ')
    info = 'Please wait...'
    flash(info)
    cmdS = f"smng@{cmds[0]}:{cmds[1]}@{g.user['level']}"
    info = SocketFunc(cmd=cmdS).client_side()
    flash(info)
    return redirect(url_for('api.advance_manager'))
















