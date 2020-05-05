# -*- coding: utf-8 -*-
# !/usr/bin/python3.7
# from server_side.models.model import *
from models.model import *


def execute_cmds():
    """
    :param: data: is a string contains command and its param with values. It should be like: 'cmd@param:vlue@param:value'
    :return: a certain result depend on the command that executed.
    """
    ssl_sockets = SocketFunc(addr_p=('0.0.0.0', 12000)).server_side()
    info = None
    while True:
        c, a = ssl_sockets.accept()
        data = str(c.recv(8192), 'utf-8')
        dataList = data.split('@')
        print(data, dataList, '\n', c, a)
        if str(dataList[0]) == 'server start':
            """
            start server
            string should be like 'server start@gameid'
            """
            info = AdvanceServerManager(targetserverid=dataList[1]).start_existed_server()

        elif str(dataList[0]) == 'server stop':
            """
            stop server.
            """
            info = AdvanceServerManager(targetserverid=dataList[1]).stop_existed_server()

        elif str(dataList[0]) == 'guid':
            """
            change admin white block list.
            The cmd string like : 'guid@adminlist:KU_id@userlevel@server_basedir'
            the server_basedir generally equals to the name of container.
            """
            paramList = dataList[1].split(':')
            if paramList[0] == 'get':
                """
                WARNING: THE string here must be like:'guid@get:adminlist@userlevel@server_basedir'
                """
                info = AdvanceServerManager(server_base_dir=dataList[3], usergameidclass=paramList[1]).get_user_game_id()
            elif paramList[0] == 'remove' and int(dataList[2]) >= 3:
                """
                string here should be like : 'guid@remove:adminlist KUcode@userlevel@server_basedir'
                """
                cls = paramList[1].split(' ')[0]
                kuid = paramList[1].split(' ')[1]
                print(paramList)
                info = AdvanceServerManager(usergameid=kuid, usergameidclass=cls, server_base_dir=dataList[3]).remove_user_game_id()
                print(info)
            else:
                if int(dataList[2]) >= 2:
                    info = AdvanceServerManager(usergameidclass=paramList[0], usergameid=paramList[1], server_base_dir=dataList[3]).set_user_game_id()
                else:
                    info = 'Invalid command or Authority.'

        elif str(dataList[0]) == 'smng':
            """
            commands that get server infos, make server a log, backup a game server dir.
            The cmd string like : 'smng@server_infos:dsls@userlevel'
            """
            paramList = dataList[1].split(':')
            if paramList[0] == 'server_infos' and int(dataList[2]) >= 1:
                print(paramList[1])
                info_ = AdvanceServerManager(callwhich=paramList[1]).return_infos()
                info = ''
                for i in info_:
                    info += f'{i}@'
            elif paramList[0] == 'server_log_dir' and int(dataList[2]) >= 3:
                info = ServerLogResolve().get_server_log()[0]
            elif paramList[0] == 'backup_servers' and int(dataList[2]) >= 2:
                info = AdvanceServerManager().backup_dst_server()
            else:
                info = 'Invalid command or Authority.'

        elif str(dataList[0]) == 'modm':
            """
            commands that manage mod in database.
            mod manager. the string should be like: 'modm@param^value@level'
            """
            paramList = dataList[1].split('^')
            print(paramList)
            if paramList[0] == 'add_mod_to_db' and int(dataList[2]) >= 2:
                """
                value string should be like:'modname&&modurl'
                """
                info = ModManager(mod_list_db=paramList[1]).add_to_database()
                print(info)
            elif paramList[0] == 'mod_db_remove' and int(dataList[2]) >= 3:
                """
                value string should be like:'modid'
                """
                info = ModManager(mod_list=paramList[1]).remove_mods_in_database()
            elif paramList[0] == 'mod_db_statue' and int(dataList[2]) >= 2:
                """
                value string should be like: 'modid 0' or 'modid 1'
                """
                info = ModManager(mod_list_db_statue=paramList[1]).change_mod_db_statue()

            elif paramList[0] == '':
                pass

        elif str(dataList[0]) == 'smodm':
            """
            commands that manage mods in a certain game server.
            command string should be like : 'smodm@param:value@userlevel'
            """
            paramList = dataList[1].split(':')
            if paramList[0] == 'mods_not_use':
                """
                value string should be like: 'gname# ', the mod_id_str should be split by space.
                :return mod ids not and names not baned and not in use split by space.
                """
                modsInUseId = ModManager(server_base_dir=paramList[1].split('#')[0]).list_mods_in_use()[1]
                db = get_db_dict()
                db.execute('SELECT * FROM mods WHERE mod_ban=%s', (1,))
                modsInDb = db.fetchall()
                notIn = ''
                for i in modsInDb:
                    if i['mod_id'] not in modsInUseId:
                        notIn += f"{i['mod_id']}^^{i['mod_name']}!!"
                db.close()
                info = notIn

            elif paramList[0] == 'mods_in_use':
                """
                value string should be like: 'gname# ', the mod_id_str should be split by space.
                :return mod ids in use split by space.
                """
                info_ = ModManager(server_base_dir=paramList[1].split('#')[0]).list_mods_in_use()
                info = f'{info_[1]}!!{info_[0]}'

            elif paramList[0] == 'add_mod':
                pass

        elif str(dataList) == 'logs':
            """
            Command string should be like: 'logs@param:value@userlevel'
            """
            paramList = dataList[1].split(':')


        elif str(dataList[0]) == 'create_initial':
            """
            create a new server container or initial a existed one.
            """
            paramList = dataList[1]
            if paramList == 'create':
                """
                when create, the command should be like:
                'create_initial@create:servername^world_set_string^mod_set_string^cluster.ini_set^master_port^caves_port^
                userlevel'
                """
                pass

        else:
            info = 'Invalid command or Authority.'
        print(info)
        if info:
            if type(info) == type(''):
                c.send(bytes(info, 'utf-8'))
            else:
                raise TypeError('Can just handle string obj.')
        c.shutdown(1)


if __name__ == '__main__':
    execute_cmds()
