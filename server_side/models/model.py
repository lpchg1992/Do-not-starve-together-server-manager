# -*- coding: utf-8 -*-
# !/usr/bin/python3.7
import random
import time
import os
import docker
import datetime
import shutil
import re
import ssl

from socket import socket, AF_INET, SOCK_STREAM
from models.db import commit_sql, get_db_dict
# from server_side.models.db import commit_sql, get_db_dict
# from flask import session

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
    :param str: a combine of strings split by space that you want to judge if it is already in a file line.
    :param dir: the dir of the file that you want to search.
    :return: a: list of strings that not in the file.
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
            shutil.rmtree(i)
            y += 1
        else:
            x += 1
    if x > 0:
        info = f'{x} failed and {y} success.'
    else:
        info = f'{y} dir or file deleted!'
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
    with open(fileDir, 'r') as f:
        fileList = f.readlines()
    fLIndexN = 0
    nLIndexN = 0
    if os.path.isfile(fileDir):
        # save changes to the list.
        for p in patternList:
            if p:
                for i in fileList:
                    if i:
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
                if i:
                    f.write(i)
        info = 'Success!'
    else:
        info = 'Invalid file dir.'
    return info


def docker_id_to_obj(gid):
    client = docker.from_env()
    c = client.containers.get(gid)
    return c


class AdvanceServerManager:
    """
    manage existed dst server, function list:
    """
    def __init__(self,
                 since=None,
                 until=None,
                 serverstatus=None,
                 callwhich='dsl',
                 targetserverid=None,
                 usergameidclass='',
                 usergameid='',
                 cluster_need_to_change='',
                 server_base_dir='DoNotStarveTogether',
                 target_bakcup_dir=''
                 ):
        """
        :param server_base_dir: equals to the name of server name.
        :param cluster_need_to_change: a string contains several params and its values split by space for cluster.ini
        like 'param:value param2:value2'
        :param usergameid: a string that contains several user KU id that split by space.
        :param usergameidclass: the type of the user game id that you want to change ==> adminlist whitelist blocklist
        :param since: a datetime object. the start time of a evnet
        :param until: a datetime object. the end of the time of a evnet
        :param targetserverid: a target docker container id.
        :param callwhich: select a list to return. dsl=all container objects of dst server. dsls=all container id strings of dst server. dsle dslr dslse dslsr
        :param target_bakcup_dir: a back up dir that need to be handled.
        :param serverstatus: describe the statue of the server. None equals all server, True equals running server, False equals exited server.
        """
        self.client = docker.from_env()
        self.dockers = self.client.containers.list(all='true')
        # image id
        self.iid = 'sha256:17405ae407ed0cb9d813eacbd6140290df0f44b819771930224a3a29198c9fe7'
        # all container objects of dst server.
        self.dstServerLists = [
            l_ for l_ in self.dockers if l_.image.id == self.iid
        ]
        # all container id strings of dst server.
        self.dstServerListsS = [
            l_.id + ' ' + l_.status + ' ' + l_.name for l_ in self.dockers
            if l_.image.id == self.iid
        ]
        # exited game server container object
        self.dSLE = [l_ for l_ in self.dstServerLists if l_.status == 'exited']
        # running game server container object
        self.dSLR = [
            l_ for l_ in self.dstServerLists if l_.status == 'running'
        ]
        # exited game server container id
        self.dSLSE = [
            id_.split(' ')[0] for id_ in self.dstServerListsS
            if id_.split(' ')[1] == 'exited'
        ]
        # running game server container id
        self.dSLSR = [
            id_.split(' ')[0] for id_ in self.dstServerListsS
            if id_.split(' ')[1] == 'running'
        ]

        self.baseDir = f'/root/.klei/DoNotStarveTogether/{server_base_dir}'
        self.backupDirPattern = 'Cluster_1\+\d{4}\-\d{2}-\d{2}\+\d{2}\:\d{2}\:\d{2}\.\d*'
        self.templatesDir = '/root/dsttemplates'
        self.clusterBaseDir = f'{self.baseDir}/Cluster_1'
        self.backupDir = f'{self.baseDir}/backup'
        self.serverStatus = serverstatus
        self.callWhich = callwhich
        self.targetServerId = targetserverid
        self.since = since
        self.until = until
        self.userGameId = usergameid
        self.userGameIdClass = usergameidclass
        self.clusterNeedToChange = cluster_need_to_change
        self.targetBackupDir = target_bakcup_dir

    def return_infos(self):
        """
        :return: a certain list or string initialized by this class
        """
        if self.callWhich == 'dsl':
            return self.dstServerLists
        elif self.callWhich == 'dsls':
            return self.dstServerListsS
        elif self.callWhich == 'dsle':
            return self.dSLE
        elif self.callWhich == 'dslr':
            return self.dSLR
        elif self.callWhich == 'dslse':
            return self.dSLSE
        elif self.callWhich == 'dslsr':
            return self.dSLSR
        else:
            return None

    def start_existed_server(self):
        """
        start existed server.
        :return: a result.
        """
        if not self.targetServerId:
            sList = self.dSLE
            for i in sList:
                i.start()
            info = 'Start server success!'
        else:
            sList = docker_id_to_obj(self.targetServerId)
            if sList and sList.status == 'exited':
                sList.start()
                info = 'Start server success!'
            else:
                info = 'No server need to be started.'
        return info

    def stop_existed_server(self):
        """
        stop existed server.
        :return: a result.
        """
        if not self.targetServerId:
            sList = self.dSLR
            for i in sList:
                i.stop()
            info = 'Stop server success!'
        else:
            sList = docker_id_to_obj(self.targetServerId)
            if sList and sList.status == 'running':
                sList.stop()
                info = 'Stop server success!'
            else:
                info = 'No server need to be stopped.'
        return info

    def backup_dst_server(self):
        """
        back up server files only when servers are stopped.
        :return:
        """
        # make sure that the backup dir existed.
        if not os.path.exists(self.backupDir):
            os.makedirs(self.backupDir)
        fileDir = self.clusterBaseDir
        dateStr_ = f'{datetime.datetime.now()}'
        dateStr__ = dateStr_.split(' ')
        dateStr = dateStr__[0] + '+' + dateStr__[1]
        targetDir = f"{self.backupDir}/Cluster_1+{dateStr}"
        if not self.dSLR:
            if os.path.exists(fileDir) and not os.path.exists(targetDir):
                shutil.copytree(fileDir, targetDir)
                time_ = f'{datetime.datetime.now()}'.split('.')[0]
                info = f'backup on {time_} successfully.'
            else:
                info = 'Invalid dir path.'
        else:
            info = "Can't backup when there are running servers! You may stop servers and try again!"
        return info

    def delete_backup(self):
        """
        delete a certain backup dir by self.targetBackupDir.
        :return: a result.
        """
        if os.path.isdir(self.targetBackupDir):
            shutil.rmtree(self.targetBackupDir)
            info = 'Delete the backup success!'
        else:
            info = 'No such backup file!'
        return info

    def get_backup_dir_list(self):
        """
        Get a list of backup dirs by create time in DES order.
        :return: dir path and its created time strings split by '!!'.
        """
        if os.path.exists(self.backupDir):
            dirGenerator = os.walk(self.backupDir)
            dirDict = {}
            for root, dirs, files in dirGenerator:
                for i in dirs:
                    if re.match(self.backupDirPattern, i):
                        path_ = os.path.join(root, i)
                        dirDict[f'{os.path.getctime(path_)}'] = path_
            # This is a iterator.
            keysG = dirDict.keys()
            keysL = []
            dirListByTime = ''
            for i in keysG:
                keysL.append(i)
            keysL.sort(reverse=True)
            for i in keysL:
                """
                dirDict[i]: the dir path; i: the dir created time.
                """
                infos = f'{dirDict[i]}##{i}'
                dirListByTime += f'{infos}!!'
        else:
            dirListByTime = 'None'

        return dirListByTime

    def set_user_game_id(self):
        """
        change user game identity.
        :return: a result.
        """
        info = None
        if self.userGameIdClass == 'adminlist':
            fileDir = self.baseDir + '/Cluster_1/adminlist.txt'
        elif self.userGameIdClass == 'whitelist':
            fileDir = self.baseDir + '/Cluster_1/whitelist.txt'
        elif self.userGameIdClass == 'blocklist':
            fileDir = self.baseDir + '/Cluster_1/blocklist.txt'
        else:
            fileDir = ''
        if fileDir and self.userGameId:
            text = str_not_in_file(self.userGameId, fileDir)
            with open(fileDir, 'a') as f:
                for i in text:
                    if i:
                        f.write(i + '\n')
                        info = 'Success!'
                    else:
                        info = 'Error: Empty data!'
        else:
            info = 'No such identity type or no user game id!'
        return info

    def set_user_game_id_from_log(self):
        pass

    def get_user_game_id(self):
        if self.userGameIdClass == 'adminlist':
            fileDir = self.baseDir + '/Cluster_1/adminlist.txt'
        elif self.userGameIdClass == 'whitelist':
            fileDir = self.baseDir + '/Cluster_1/whitelist.txt'
        elif self.userGameIdClass == 'blocklist':
            fileDir = self.baseDir + '/Cluster_1/blocklist.txt'
        else:
            fileDir = ''
        listString = ''
        if fileDir:
            with open(fileDir, 'r') as f:
                listIter = f.readlines()
            for i in listIter:
                listString += f'{i} '
        return listString

    def remove_user_game_id(self):
        if self.userGameIdClass == 'adminlist':
            fileDir = f'{self.clusterBaseDir}/adminlist.txt'
        elif self.userGameIdClass == 'whitelist':
            fileDir = f'{self.clusterBaseDir}/whitelist.txt'
        elif self.userGameIdClass == 'blocklist':
            fileDir = f'{self.clusterBaseDir}/blocklist.txt'
        else:
            fileDir = ''
        idS = self.userGameId.split(' ')
        patterns = ''
        lines = ''
        for i in idS:
            if i:
                patterns += f'{i}()'
                lines += '@@'
        info = update_file_lines(fileDir, patterns, lines, 2)
        return info

    def set_cluster_config(self):
        """
        configure cluster.ini file.
        :return: a result.
        """
        if not self.dSLR:
            patterns = ''
            new_lines = ''
            baseList = self.clusterNeedToChange.split(' ')
            paramList = [i.split(':')[0] for i in baseList]
            valueList = [i.split(':')[1] for i in baseList]
            for p in paramList:
                line = f'{p} = {valueList[paramList.index(p)]}\n@@'
                pattern = f'{p}'
                patterns += pattern
                new_lines += line
            if patterns and new_lines:
                path = f'{self.clusterBaseDir}/Master/cluster.ini'
                info = update_file_lines(path, patterns, new_lines) + 'Need restart to make it effective.'
            else:
                info = 'Wrong value! No config can be change!'
        else:
            info = "Can't change Config files When servers running!"
        return info


class ServerLogResolve(AdvanceServerManager):
    def __init__(self, target_log):
        """
        server log resolve tools
        :param target_log:a log dir path.
        """
        super().__init__()
        self.targetLog = target_log

    def get_server_log(self):
        """
        Return a log file dir of a certain dst server.
        :return: a dir of a log file
        """
        if not self.until:
            self.until = datetime.datetime.now()
        if not self.since:
            self.since = self.until + datetime.timedelta(days=-100)
        dir_ = '/root/server_side/glogs'
        dirList = []
        if not self.targetServerId:
            sList = self.dstServerLists
        else:
            sList = self.targetServerId
        if sList and self.since and self.until:
            for i in sList:
                dirName = dir_ + '/' + i.name + '##' + f'{datetime.datetime.now()}'.split('.')[0] + '.log'
                dirList.append(dirName)
                logStr = i.logs(since=self.since, until=self.until)
                logList = logStr.decode('utf-8').split('\n')
                with open(dirName, 'w') as f:
                    for t_ in logList:
                        f.write(t_ + '\n')
            return dirList
        else:
            return []

    def get_log_dirs(self):
        """
        get game log dirs.
        :return: a list contains several log paths
        """
        dir_ = '/root/server_side/glogs'
        dirGenerator = os.walk(dir_)
        pathList = []
        for root, dirs, files in dirGenerator:
            for i in files:
                path_ = os.path.join(root, i)
                pathList.append(path_)
        return pathList

    def resolve_game_log_user(self):
        """
        resolve game logs for login users.
        :return: return game user login infos. contains: steamID, KU_code, role chosen.
        """
        userLoginList = []
        userRoleList = []
        if os.path.isfile(self.targetLog):
            with open(self.targetLog) as f:
                contentList = f.readlines()
        for i in contentList:
            if re.search('Client authenticated', i):
                user = i.split(' ')
                """
                user[2]:steam nick name. user[1]:KU_code.
                """
                userInfos = "%s %s" % (user[2].strip('\n'), user[1].strip('()'))
                userLoginList.append(userInfos)
            if re.search('Spawn request', i):
                """
                user[3]steam nick name, user[1] the role.
                """
                user = i.split(' ')
                userRole = '%s %s' % (user[3].strip("\n"), user[1])
                userRoleList.append(userRole)
        userStr = ''
        for i in userLoginList:
            for j in userRoleList:
                if re.search(i.split(' ')[0], j.split(' ')[0]):
                    userStr += f'{i} {j.split(" ")[1]}'
                else:
                    userStr += f'{i} '
        return userStr

    def resolve_game_log_chat(self):
        """
        resolve chat in log.
        :return: a chat log.
        """
        pass

    def resolve_log_stream(self):
        """
        resolve a log stream ogj.
        :return:
        """
        pass


class ModManager(AdvanceServerManager):
    def __init__(self,
                 mod_list='',
                 mod_list_db='',
                 mod_list_db_statue='',
                 server_base_dir='DoNotStarveTogether',
                 targetserverid=''
                 ):
        """
        This Class is a mod manager.
        :param mod_list_db_statue: a string contains a mod's id and its statue that need to change.
        like 'modid statue'
        :param mod_list: a string contains several mod ids split by space.
        :param mod_list_db: a string contains a mod's infos.
        It should be look like: 'modname&&modurl'
        """
        super().__init__(server_base_dir=server_base_dir, targetserverid=targetserverid)
        self.modLists = mod_list
        self.setUpFileDir = self.clusterBaseDir + '/mods/dedicated_server_mods_setup.lua'
        self.overridesFileDir = self.clusterBaseDir + '/Master/modoverrides.lua'
        self.modListDb = mod_list_db
        self.modListDbStatue = mod_list_db_statue

    def list_mods_in_use(self):
        """
        :return: a list contains name and id. name split by '^^'.
        """
        with open(self.overridesFileDir, 'r') as f:
            testList = f.readlines()
        modListName = ''
        modListId = ''
        modIds = []
        for i in testList:
            if '["workshop-' in i:
                modId = i.split('"')[1].split('-')[1]
                modIds.append(modId)
        db = get_db_dict()
        for j in modIds:
            db.execute('SELECT * FROM mods WHERE mod_id = %s', (j,))
            result = db.fetchone()
            if result:
                modListName += f"{result['mod_name']}^^"
                modListId += f"{result['mod_id']} "
        db.close()
        return [modListName, modListId]

    def add_mod(self):
        """
        Add mod id to all mod files.
        :return: a result.
        """
        if not self.dSLR:
            caveDir = self.clusterBaseDir + '/Caves/modoverrides.lua'
            if os.path.isfile(caveDir):
                os.remove(caveDir)
            modList = self.modLists.split(' ')
            with open(self.setUpFileDir, 'r') as f:
                setUpFileList = f.readlines()
            with open(self.overridesFileDir, 'r') as f:
                overridesFileList = f.readlines()
            if overridesFileList[0] != 'return{\n':
                overridesFileList.insert(0, 'return{\n')
            if overridesFileList[-1] != '}\n':
                overridesFileList.append('}\n')
            j = str(setUpFileList)
            k = str(overridesFileList)
            for i in modList:
                if i not in j:
                    newMod = f'ServerModSetup("{i}")\n'
                    setUpFileList.append(newMod)
                if i not in k:
                    newMod = '  ["workshop-%s"]={enabled=true } ,\n' % i
                    overridesFileList.insert(-1, newMod)
            with open(self.setUpFileDir, 'w') as f:
                for i in setUpFileList:
                    if bool(i):
                        f.write(i)
            with open(self.overridesFileDir, 'w') as f:
                for i in overridesFileList:
                    if bool(i):
                        f.write(i)
            shutil.copyfile(self.overridesFileDir, caveDir)
            info = 'Change mod files Success!'
        else:
            info = "Can't add mod when servers are running."
        return info

    def recreate_mod_file(self):
        """
        replace a mod id.
        :return: a result.
        """
        if not self.dSLR:
            overDirM = self.clusterBaseDir + '/Master/modoverrides.lua'
            overDirC = self.clusterBaseDir + '/Caves/modoverrides.lua'
            setDir = self.clusterBaseDir + '/mods/dedicated_server_mods_setup.lua'
            modList = self.modLists.split(' ')
            with open(overDirM, 'w') as f:
                f.write('return {\n')
                for i in modList:
                    line = '  ["workshop-%s"]={enabled=true } ,\n' % i
                    f.write(line)
                f.write('}\n')
            if os.path.isfile(overDirC):
                os.remove(overDirC)
            shutil.copyfile(overDirM, overDirC)
            with open(setDir, 'w') as f:
                for i in modList:
                    line = f'ServerModSetup("{i}")\n'
                    f.write(line)
            info = 'Create mod related files success!'
        else:
            info = "Can't Recreate mod related files when servers are running!"
        return info

    def delete_mod(self):
        """
        This function can just be used for NEW server. Delete target mod id in all mod files.
        :return: a result.
        """
        if not self.dSLR:
            modList = self.modLists.split(' ')
            ModPatterns = ''
            ModLines = ''
            for i in modList:
                Pattern = i
                Line = '@@'
                ModPatterns += Pattern
                ModLines += Line
            setMod = update_file_lines(self.setUpFileDir, ModPatterns, ModLines, 2)
            overMod = update_file_lines(self.overridesFileDir, ModPatterns, ModLines, 2)
            info = f"set up file: {setMod}, overrides file: {overMod}"
        else:
            info = "Can't delete mod id when servers are running."
        return info

    def add_to_database(self):
        """
        Add mods to database.
        :return: a result.
        """
        baseList = self.modListDb.split('&&')
        ec = 0
        eMod = ''
        errorInfo = None
        id = baseList[1].split('=')[1]
        if '&' in id:
            id = id.split('&')[0]
        db = get_db_dict()
        db.execute('SELECT * FROM mods WHERE mod_id = %s', (id,))
        ifIn = db.fetchone()
        db.close()
        if not ifIn:
            try:
                commit_sql('INSERT INTO mods (mod_id, mod_url, mod_name)' ' VALUES (%s, %s, %s)',
                           (id, baseList[1], baseList[0],))
            except Exception:
                ec += 1
                eMod += self.modListDb
            if ec:
                errorInfo = f'Failed times {ec}, mods {eMod}'
            info = f'Add to database Success!{errorInfo}'
        else:
            info = 'Already added!'
        return info

    def remove_mods_in_database(self):
        """
        Delete several mods
        :return: a result.
        """
        modIDs = self.modLists.split(' ')
        c = 0
        db = get_db_dict()
        for i in modIDs:
            db.execute('SELECT * FROM mods WHERE mod_id = %s', (i,))
            r = db.fetchone()
            if r:
                commit_sql('DELETE FROM mods WHERE mod_id = %s', (i,))
                c += 1
            else:
                c = 0
        db.close()
        info = f'{c} mods removed.'
        return info

    def change_mod_db_statue(self):
        """
        ban or active a mod.
        :return: a result.
        """
        info = 'Did nothing.'
        infoList = self.modListDbStatue.split(' ')
        if infoList[1] == '0':
            commit_sql('UPDATE mods SET mod_ban = %s WHERE mod_id = %s', (0, infoList[0]))
            info = f'Ban the mod {infoList[0]} success!'
        elif infoList[1] == '1':
            commit_sql('UPDATE mods SET mod_ban = %s WHERE mod_id = %s', (1, infoList[0]))
            info = f'Activate the mod {infoList[0]} success!'
        return info


class DstServerCreator(ModManager):
    """
    create new dst server
    """
    def __init__(self,
                 from_new_backup='new',
                 from_backup_dir=None,
                 if_start_right_now=False,
                 world_need_to_change='',
                 server_base_dir='',
                 targetserverid=''
                 ):
        """
        :param world_need_to_change: a string contains several params and its values split by space for worldgenoverrides file.
        like 'param:value param2:value2'
        :param from_backup_dir: the dir for function create_from_backups
        :param from_new_backup: create a new server or from a backup. new or backup.
        :param if_start_right_now: True or False.
        """
        super().__init__(server_base_dir=server_base_dir, targetserverid=targetserverid)
        self.worldOverrideTemplate = self.baseDir + ''
        self.fromNewBackup = from_new_backup
        self.fromBackupDir = from_backup_dir
        self.ifStartRightNow = if_start_right_now
        self.worldNeedToChange = world_need_to_change

    def create_from_backups(self):
        """
        Restore a backup game server file.
        :return: a result.
        """
        if self.fromNewBackup == 'backup' and os.path.exists(self.clusterBaseDir):
            remove_file_dir(self.clusterBaseDir)
            if os.path.exists(self.fromBackupDir) and not os.path.exists(self.clusterBaseDir):
                shutil.copytree(self.fromBackupDir, self.clusterBaseDir)
                if self.ifStartRightNow:
                    self.start_existed_server()
                    info = 'Created and started game server from backup.'
                else:
                    info = 'Created game server from backup. You may start the server now.'
                return info
            else:
                return 'Invalid dir path.'
        else:
            return 'Invalid initial value!'

    def set_world_config(self):
        """
        configure the world override file.
        :return: a result.
        """
        if self.fromNewBackup == 'new':
            patterns = ''
            new_lines = ''
            baseList = self.worldNeedToChange.split(' ')
            paramList = [i.split(':')[0] for i in baseList]
            valueList = [i.split(':')[1] for i in baseList]
            for p in paramList:
                line = f'\t\t{p} = "{valueList[paramList.index(p)]}",\n@@'
                pattern = f'\t\t{p}\ \=\ ()'
                patterns += pattern
                new_lines += line
            if patterns and new_lines:
                path = f'{self.clusterBaseDir}/Master/worldgenoverride.lua'
                info = update_file_lines(path, patterns, new_lines)
            else:
                info = 'Wrong value! No config can be change!'
        else:
            info = 'Wrong initial value! from_new_backup must be new.'
        return info

    def initial_server(self):
        """
        Initial a game server with the old configs.
        :return: a result.
        """
        if self.fromNewBackup == 'new':
            removeDir = f'{self.clusterBaseDir}/Master/save {self.clusterBaseDir}/Master/backup ' \
                        f'{self.clusterBaseDir}/Caves/save {self.clusterBaseDir}/Caves/backup ' \
                        f'{self.clusterBaseDir}/Master/server_chat_log.txt {self.clusterBaseDir}/Master/server_log.txt ' \
                        f'{self.clusterBaseDir}/Caves/server_chat_log.txt {self.clusterBaseDir}/Caves/server_log.txt'
            remove_file_dir(removeDir)
            self.start_existed_server()
            return 'initial server success!'
        else:
            return 'Wrong initial value!'

    def create_new_server(self):
        pass


class WebSiteManager:
    """
    manage website user and configuration
    """
    def __init__(self):
        pass

    def list_users(self):
        pass


class SocketFunc:
    def __init__(self, addr_p=('120.77.152.132', 11007), cmd=None):
        self.addr_p = addr_p
        self.cmd = cmd

    def server_side(self):
        """
        server side.
        :return: a ssl socket object.
        """
        s = socket(AF_INET, SOCK_STREAM)
        s.bind(self.addr_p)
        s.listen(5)

        # Wrap with an SSL layer requiring client certs
        s_ssl = ssl.wrap_socket(s,
                                keyfile=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'key.pem'),
                                certfile=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'cert.pem'),
                                server_side=True
                                )
        return s_ssl



