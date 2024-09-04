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
    """
    DataStore-Dump: {
    'Shellyplug-083A8DF437C7':     {'Commons': {
                                        'CURRENT_DATA': 0, 
                                        'lastUPD': datetime.datetime(2024, 9, 4, 18, 0, 23, 899967), 
                                        'TIMEOUT': 0, 
                                        'RELOAD_TIMEOUT': 0, 
                                        'CSV_FORMAT': 'MULTI', 
                                        'YML_FORMAT': 'SINGLE', 
                                        'devdata': {
                                            'Type': 'SHPLG2-1', 
                                            'Hardware': 'Shelly', 
                                            'Modul': 'SHPLG2-1', 
                                            'Time': 5, 'Format': 'json', 
                                            'InfoURL': 'settings', 
                                            'Retry': 3, 
                                            'IP': '192.168.2.136', 
                                            'name': 'None', 
                                            'hostname': 'None', 
                                            'dBlock': {
                                                'modul': <module 'SHPLG2-1' from '/Users/ralphfollrichs/Projects/hoco/progs/SHPLG2-1.py'>, 
                                                'driver': <SHPLG2-1.driver object at 0x10628d850>}, 
                                                'devhandler': <devhandler.DevHandler object at 0x10628dd90>}, 
                                        'WEB': [
                                            ['ESP Infos', 'Devider', 'DIV_DATA'], 
                                            ['Name', 'name', 'CURRENT_DATA'], 
                                            ['Hostname', 'hostname', 'CURRENT_DATA'], 
                                            ['IP', 'IP', 'CURRENT_DATA']], 
                                        'RRD_DB': [[
                                            ['OUTFILE', 'CONST', 'Shellyplug-083A8DF437C7'], 
                                            ['SELF', '§Power', 'CURRENT_DATA']]], 
                                        'header': 'time', 
                                        'Active': True, 
                                        'Flag': False, 
                                        'Counter': 8, 
                                        'initTime': datetime.datetime(2024, 9, 4, 18, 0, 18, 189573), 
                                        'Service': <DataStore.Service object at 0x106256f40>}, 
                                    'Devider': {
                                        'CURRENT_DATA': 0, 
                                        'lastUPD': None, 
                                        'DIV_DATA': '- - - - >'}, 
                                    'Power': {
                                        'CURRENT_DATA': 11.56, 
                                        'lastUPD': None}, 
                                    'name': {
                                        'CURRENT_DATA': 0, 'lastUPD': None}, 
                                    'hostname': {
                                        'CURRENT_DATA': 0, 'lastUPD': None}, 
                                    'IP': {
                                        'CURRENT_DATA': 0, 'lastUPD': None}}, 

    """