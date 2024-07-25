###############################################################
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################
import datetime
import logging 
import os
import socket
import yaml
import time

import config as cfg
import devhandler as dh

logger = logging.getLogger(__name__)

        
if __name__ == '__main__':
    current_file_path = os.path.realpath(__file__)
    current_file_name = os.path.basename(current_file_path)

    cfg.init(current_file_name)
    x = datetime.datetime.now()

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s :: %(levelname)-7s :: [%(name)+15s] [%(lineno)+3s] :: %(message)s',
        datefmt=cfg.ini['debugdatefmt'],
        handlers=[
            logging.FileHandler(f"{cfg.ini['LogPath']}/{current_file_name[:-3]}_{socket.gethostname()+x.strftime(cfg.ini['logSuffix'])}.log"),
            logging.StreamHandler()
        ])

    logger.info("")
    logger.info(f'---------- starting {current_file_path} ----------') 

    ServerName = cfg.ini['DaboServerName']
    ServerPort = cfg.ini['DaboServerPort']
    #server = HTTPServer((ServerName, ServerPort), webserverHandler)
    logger.info(f"Device server started on {socket.getfqdn()}")
    
    with open(f"{cfg.ini['YMLPath']}/devs.yml", 'r') as ymlfile:
        DevList = yaml.safe_load(ymlfile)
    logger.debug(DevList)
    
    for netname in DevList:
        print(netname)
        try:
            DevList[netname]['eps']
            DevList[netname]['format']
        except KeyError as err:
            logger.error(f"{err} not specified for {netname}")
            continue
        DevList[netname]['devhandler'] = dh.DevHandler(f"{netname}.local", DevList[netname])
        if DevList[netname]['devhandler'].iBlock['isonline']:
            for ep in DevList[netname]['eps']:
                DevList[netname][ep] = DevList[netname]['devhandler'].read(ep)
    while True:
        time.sleep(10)