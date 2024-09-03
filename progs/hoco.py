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
import DataStore as ds

logger = logging.getLogger(__name__)

        
if __name__ == '__main__':
    current_file_path = os.path.realpath(__file__)
    current_file_name = os.path.basename(current_file_path)

    cfg.init(current_file_name)
    x = datetime.datetime.now()

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s :: %(levelname)-7s :: [%(name)+16s] [%(lineno)+3s] :: %(message)s',
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
    
    cfg.ini['Dstore'] = ds.DS(f"{cfg.ini['YMLPath']}/{cfg.ini['yml']['files']['DATASTORE_YML']}") ######
    #    ini['Dstore'] = ds.DS(f"{ini['YMLPath']}/{yml['files']['DATASTORE_YML']}") ######
    
    with open(f"{cfg.ini['YMLPath']}/devdata.yml", 'r') as ymlfile:
        DevList = yaml.safe_load(ymlfile)
    #logger.debug(DevList)
    
    reachable = 0
    unreachable = 0

    for device in ds.DS.ds.items():
        hostname = device[0]
        devdata = device[1]['Commons']['devdata']
        logger.info(f"processing device: {hostname}")    
        print(devdata)
        try:
            devdata['InfoURL']
            devdata['Format']
        except KeyError as err:
            logger.error(f"{err} not specified for {hostname}")
            continue
        devdata['devhandler'] = dh.DevHandler(hostname)
        logger.debug(ds.DS.ds)
            
    logger.info(f"got {reachable} devices and {unreachable} unreachable device(s)")
    while True:
        time.sleep(10)
