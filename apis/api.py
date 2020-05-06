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

from datetime import datetime

# from urllib.parse import quote, unquote

bp = Blueprint('api', __name__)


@bp.route('/', methods=('GET', 'POST'))
@login_required
def index():
    return redirect(url_for('api.manager_index'))


@bp.route('/manager_index')
@login_required
def manager_index():
    """
    a game server list.
    :return:
    """
    userlevel_ = int(g.user['level'])
    return render_template('manager_index.html', userlevel=userlevel_)


@bp.route('/start_dst_server/<gid>')
@login_required
def start_dst_server(gid):
    """
    start a certain game server by its id.
    :param gid: the game server id.
    :return:
    """
    if int(g.user['level']) >= 1:
        info = SocketFunc(cmd=f'server start@{gid}').client_side()
    else:
        info = 'Sorry, Do not have the Authority!'
    flash(info)
    return redirect(url_for('api.manager_index'))


@bp.route('/stop_dst_server/<gid>')
@login_required
def stop_dst_server(gid):
    """
    stop a a game server by its id.
    :param gid: the game server id.
    :return:
    """
    if int(g.user['level']) >= 1:
        info = SocketFunc(cmd=f'server stop@{gid}').client_side()
    else:
        info = 'Sorry, Do not have the Authority!'
    flash(info)
    return redirect(url_for('api.manager_index'))


@bp.route('/server_manager/<gid>/<gname>')
@login_required
def server_manager(gid, gname):
    """
    a certain game server manager index.
    :param gid: the game server id.
    :param gname: the game server name.
    :return: None.
    """
    return render_template('server_manager.html', gname=gname, gid=gid, userlevel=int(g.user['level']))


@bp.route('/create_initial/<cmdtype>/<gname>/<gid>')
@login_required
def create_initial(cmdtype, gname, gid):
    """
    game create configure and initial tools.
    :param cmdtype: the type of cmd.
    :param gname: the name of the game server.
    :param gid: the container id of the game server.
    :return: None.
    """
    if cmdtype == 'initial':
        cmd__ = f'create_initial@initial:{gname}@{g.user["level"]}'
        info = SocketFunc(cmd=cmd__).client_side()
        flash(info)
        return redirect(url_for('api.server_manager', gname=gname, gid=gid, userlevel=int(g.user['level'])))



@bp.route('/game_user_auth_list/<cls_>/<gname>/<gid>', methods=('POST', 'GET'))
@login_required
def game_user_auth_list(cls_, gname, gid):
    """
    user game identity manager index.
    :param cls_: The identity type.
    :param gname: the game server name.
    :param gid: the game server id.
    :return: None.
    """
    session['cls_'] = cls_
    session['gname'] = gname
    session['gid'] = gid
    cls = cls_
    cls___ = None
    if cls == 'adminlist':
        cls___ = '管理员名单'
    elif cls == 'whitelist':
        cls___ = '白名单'
    elif cls == 'blocklist':
        cls___ = '黑名单'

    cmd__ = f'guid@get:{cls}@{g.user["level"]}@{gname}'
    listNow_ = SocketFunc(cmd=cmd__).client_side()
    listNow = [x.strip('\n') for x in listNow_.strip().split(' ') if x]

    recentPlayer = []

    if request.method == 'POST':
        text = request.form['text']
        if not text and not cls:
            error = 'Content Should not be empty!'
            flash(error)
        else:
            cmdS = f"guid@{cls}:{text}@{g.user['level']}@{gname}"
            info = SocketFunc(cmd=cmdS).client_side()
            if info:
                flash(info)
            return redirect(url_for('api.game_user_auth_list', cls_=cls, gname=gname, gid=gid))
    return render_template('game_user_auth_list.html', cls_=cls, listnow=listNow, name=gname, cls__=cls___, userlevel=g.user['level'])


@bp.route('/guid/<kuid>/<cls>/<gname>')
@login_required
def guid(kuid, cls, gname):
    """
    user game identity manager.
    :param kuid: user KU_ code.
    :param cls: the identity type need to change.
    :param gname: the game server name.
    :return: None.
    """
    cmd__ = f'guid@remove:{cls} {kuid}@{g.user["level"]}@{gname}'
    info = SocketFunc(cmd=cmd__).client_side()
    flash(info)
    cls = session['cls_']
    gname = session['gname']
    gid = session['gid']
    return redirect(url_for('api.game_user_auth_list', cls_=cls, gname=gname, gid=gid))


@bp.route('/server_mod_manager/<gname>/<gid>')
@login_required
def server_mod_manager(gname, gid):
    """
    server mod manager index.
    :param gname: the game server name.
    :param gid: the game server id
    :return: None.
    """
    cmd__ = f'smodm@mods_not_use:{gname}# @{g.user["level"]}'
    mixInfos = SocketFunc(cmd=cmd__).client_side().split('!!')
    nUse = []
    for i in mixInfos:
        i_ = i.split('^^')
        if i_[0] and i_[1]:
            nUse.append({'id': i_[0], 'name': i_[1]})

    cmd__ = f'smodm@mods_in_use:{gname}# @{g.user["level"]}'
    mixInfos = SocketFunc(cmd=cmd__).client_side().split('!!')[1].split('^^')
    use = ''
    for j in mixInfos:
        if j:
            use += f'{j} | '

    return render_template('server_mod_manager.html', userlevel=g.user['level'], gname=gname, gid=gid, nuse=nUse, use=use)


@bp.route('/smodm/<cmdtype>/<gname>/<gid>/<mod_id>')
@login_required
def smodm(cmdtype, gname, gid, mod_id):
    """
    server mod manager
    :param cmdtype: cmd type.
    :param gname: the game server name
    :param gid: the game server id
    :param mod_id: mod id string.
    :return: None.
    """
    info = None
    if cmdtype == 'add_mod':
        cmd__ = f'smodm@add_mod:{gname}#{mod_id}@{g.user["level"]}'
        info = SocketFunc(cmd=cmd__).client_side()
    if cmdtype == 'delete_mod':
        cmd__ = f'smodm@delete_mod:{gname}#{mod_id}@{g.user["level"]}'
        info = SocketFunc(cmd=cmd__).client_side()
    if info:
        flash(info)

    cmd__ = f'smodm@mods_not_use:{gname}# @{g.user["level"]}'
    mixInfos = SocketFunc(cmd=cmd__).client_side().split('!!')
    nUse = []
    for i in mixInfos:
        i_ = i.split('^^')
        if i_[0] and i_[1]:
            nUse.append({'id': i_[0], 'name': i_[1]})

    cmd__ = f'smodm@mods_in_use:{gname}# @{g.user["level"]}'
    mixInfos = SocketFunc(cmd=cmd__).client_side().split('!!')[1].split('^^')
    use = ''
    for j in mixInfos:
        if j:
            use += f'{j} | '
    return redirect(url_for('api.server_mod_manager', userlevel=g.user['level'], gname=gname, gid=gid, nuse=nUse, use=use))


@bp.route('/backup_list/<cmdtype>/<gname>/<path>')
@login_required
def backup_list(gname, path, cmdtype):
    """
    backup manager.
    :return: None.
    """
    pathM = path.replace('\\', '/')
    cmd__ = f'backup@list^^{gname}@{g.user["level"]}'
    info_ = SocketFunc(cmd=cmd__).client_side()
    if info_ != 'None':
        backupMix = info_.split('!!')
        backups = []
        info = None
        for i in backupMix:
            if i:
                j = i.split('##')
                ctime = f'{datetime.fromtimestamp(float(j[1]))}'.split('.')[0]
                path_ = j[0].replace('/', '\\')
                backups.append({'path': path_, 'ctime': ctime})
        if cmdtype != 'None':
            if cmdtype == 'delete':
                cmd__ = f'backup@delete^^{gname}#{pathM}@{g.user["level"]}'
                info = SocketFunc(cmd=cmd__).client_side()
            elif cmdtype == 'restore':
                cmd__ = f'backup@restore^^{gname}#{pathM}@{g.user["level"]}'
                info = SocketFunc(cmd=cmd__).client_side()
            elif cmdtype == 'apply':
                pass
            elif cmdtype == 'make':
                cmd__ = f'backup@make^^{gname}@{g.user["level"]}'
                info = SocketFunc(cmd=cmd__).client_side()
            if info:
                flash(info)
            return redirect(url_for('api.backup_list', userlevel=g.user['level'], backups=backups, gname=gname, cmdtype='None', path='None'))
    else:
        backups = []
    return render_template('backup_list.html', userlevel=g.user['level'], backups=backups, gname=gname, cmdtype='None', path='None')


@bp.route('/manage_center')
@login_required
def manage_center():
    """
    Manager center index.
    :return: None
    """
    if int(g.user['level']) >= 2:
        return render_template('manage_center.html', userlevel=g.user['level'])
    else:
        info = 'Invalid Authority.'
        flash(info)
        return redirect(url_for('api.manager_index'))


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


# @bp.route('/')
















