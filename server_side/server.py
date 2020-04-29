# -*- coding: utf-8 -*-
# !/usr/bin/python3.7
from models.model import *


def execute_cmds():
    """
    :param: data: is a string contains command and its param with values. It should be like: 'cmd@param:vlue@param:value'
    :return:
    """
    ssl_sockets = SocketFunc(addr_p=('0.0.0.0', 11007)).server_side()
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
            The cmd string like : 'guid@adminlist:KU_id@userlevel'
            """
            if int(dataList[2]) >= 2:
                paramList = dataList[1].split(':')
                info = AdvanceServerManager(usergameidclass=paramList[0], usergameid=paramList[1]).set_user_game_id()
            else:
                info = 'Invalid command or Authority.'

        elif str(dataList[0]) == 'smng':
            """
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
                info = AdvanceServerManager().get_server_log()[0]
            elif paramList[0] == 'backup_servers' and int(dataList[2]) >= 2:
                info = AdvanceServerManager().backup_dst_server()
            else:
                info = 'Invalid command or Authority.'

        elif str(dataList[0]) == 'modm':
            """
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
            elif paramList[0] == 'mod_db_remove'and int(dataList[2]) >= 3:
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
