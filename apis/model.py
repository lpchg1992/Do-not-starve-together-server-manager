# -*- coding: utf-8 -*-
# !/usr/bin/python3.7
import click
import random
import time
import os
import docker
import datetime
import shutil
import re
import ssl

from socket import socket, AF_INET, SOCK_STREAM
from flask.cli import with_appcontext
from apis.db import commit_sql, get_db_dict


def generate_random():
    """
    :return: a random key
    """
    character = [
        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n',
        'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'
    ]
    num = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    total = character + num
    codeList = []
    for i in range(15):
        codeList.append(total[random.randint(0, 35)])
    code = str(time.time()) + ''.join(codeList)
    # print(code)
    return code


def str_not_in_file(str, dir):
    """
    :param str a combine of strings split by space that you want to judge if it is already in a file line.
    :param dir the dir of the file that you want to search.
    :return: a list of strings that not in the file.
    """
    with open(dir, 'r') as f_:
        dirList = [lines.strip('\n ') for lines in f_]
    strList_ = str.split(' ')
    strList = []
    for i in strList_:
        if i not in dirList:
            strList.append(i)
    return strList


def time_to_datetime_obj(timestr=''):
    """
    convert time string into datetime obj.
    :param timestr:a string like this : '2020 4 3 7 30'
    :return: right format : return datetime.datetime obj, wrong format: return Nong.
    """
    timeStr = timestr + ' 0' + ' 0'
    l_ = timeStr.split(' ')
    if len(l_) == 7:
        try:
            timeInt = [int(i_) for i_ in l_]
        except Exception:
            return None
        return datetime.datetime(timeInt[0], timeInt[1], timeInt[2],
                                 timeInt[3], timeInt[4], timeInt[5],
                                 timeInt[6])
    else:
        return None


def remove_file_dir(dir_):
    """
    Remove a file or dir.
    :param dir_: a string contains several dir that need to be removed split by space.
    :return: a result.
    """
    targetDir_ = dir_
    targetDir = targetDir_.split(' ')
    x = 0
    y = 0
    for i in targetDir:
        if os.path.isfile(i):
            os.remove(i)
            y += 1
        elif os.path.isdir(i):
            os.rmdir(i)
            y += 1
        else:
            x += 1
    if x > 0:
        info = '{x} failed and {y} success.'
    else:
        info = '{y} dir or file deleted!'
    return info


def update_file_lines(file_dir, old_line_patterns, new_lines, match_or_search=1):
    """
    update a text file line by line. This function is not for huge size files.
    :param match_or_search: if 1 use re.match method, if 2 use re.search method.
    :param file_dir: the dir of the target file.
    :param old_line_patterns: for re.match to match the target line. Contains several patterns split by '()'.
    :param new_lines: the string for updating the target line. Contains several 'strings' split by '@@'
    :return a result.
    """
    fileDir = file_dir
    matchOrSearch = match_or_search
    patternList = old_line_patterns.split('()')
    newLine = new_lines.split('@@')
    fileList = fileDir.readlines()
    fLIndexN = 0
    nLIndexN = 0
    if os.path.isfile(fileDir):
        # save changes to the list.
        for p in patternList:
            for i in fileList:
                if matchOrSearch == 1:
                    if re.match(p, i.strip('\n')):
                        fileList[fLIndexN] = newLine[nLIndexN]
                        fLIndexN += 1
                    else:
                        fLIndexN += 1
                else:
                    if re.search(p, i.strip('\n')):
                        fileList[fLIndexN] = newLine[nLIndexN]
                        fLIndexN += 1
                    else:
                        fLIndexN += 1
            nLIndexN += 1
        # write the list to the file line by line.
        with open(fileDir, 'w') as f:
            for i in fileList:
                f.write(i)
        info = 'Success!'
    else:
        info = 'Invalid file dir.'
    return info


class SocketFunc:
    def __init__(self, addr_p=('120.77.152.132', 12000), cmd=None):
        self.addr_p = addr_p
        self.cmd = cmd

    def client_side(self):
        s = socket(AF_INET, SOCK_STREAM)
        s_ssl = ssl.wrap_socket(s, cert_reqs=ssl.CERT_REQUIRED, ca_certs=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'cert.pem'))
        E = None
        feedBack = None
        try:
            s_ssl.connect(self.addr_p)
        except Exception as e:
            E = e
        try:
            s_ssl.send(bytes(self.cmd, 'utf-8'))
        except Exception as e:
            E = e
        try:
            feedBack = str(s_ssl.recv(8192), 'utf-8')
        except Exception as e:
            E = e
        if E:
            s_ssl.shutdown(0)
            s_ssl.close()
            return f'A error. Details:{E}'
        else:
            s_ssl.shutdown(0)
            s_ssl.close()
            return feedBack



@click.command('key-0')
@with_appcontext
def generate_random_key_a():
    for i in range(2):
        key_ = generate_random() + '+0'
        commit_sql('INSERT INTO invite_code (code)' ' VALUES (%s)', (key_, ))


@click.command('key-1')
@with_appcontext
def generate_random_key_b():
    for i in range(2):
        key_ = generate_random() + '+1'
        commit_sql('INSERT INTO invite_code (code)' ' VALUES (%s)', (key_, ))


@click.command('key-2')
@with_appcontext
def generate_random_key_c():
    for i in range(2):
        key_ = generate_random() + '+2'
        commit_sql('INSERT INTO invite_code (code)' ' VALUES (%s)', (key_, ))


@click.command('key-3')
@with_appcontext
def generate_random_key_d():
    for i in range(2):
        key_ = generate_random() + '+3'
        commit_sql('INSERT INTO invite_code (code)' ' VALUES (%s)', (key_, ))


def init_app(app):
    app.cli.add_command(generate_random_key_a)
    app.cli.add_command(generate_random_key_b)
    app.cli.add_command(generate_random_key_c)
    app.cli.add_command(generate_random_key_d)
