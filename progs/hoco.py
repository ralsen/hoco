###############################################################
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################
import datetime
import logging 
import os
import socket
import yaml
import json
import requests

import config as cfg

logger = logging.getLogger(__name__)
logging.getLogger('urllib3').setLevel(logging.WARNING)

class DevHandle:
    def __init__(self, myDefs, hostname):
        try:
            self.ip = socket.gethostbyname(hostname)
            self.hostname = hostname
            self.myDefs = myDefs
            logger.debug(f"Die IP-Adresse von {hostname} ist {self.ip}")
        except socket.gaierror as e:
            self.isonline = False            
            logger.error(f"{hostname}: {e}")
        else:
            self.isonline = self.isDeviceOnline(self.ip)
        
    def read(self, endpoint):
        logger.debug(f"START: http://{self.ip}/{endpoint}: --------------------->")
        try:
            res = requests.get (f"http://{self.ip}/{endpoint}")
            if not res.ok:
                raise ValueError (f"endpoint was '{endpoint}'")
        except Exception as e:
            logger.error(f"cant get the Shelly data: {e}")
            return None
        if self.myDefs['format'] == "json":
            data = json.loads(res.text)
        elif self.myDefs['format'] == 'text':
            data = res.text
        else:
            logger.error(f"wrong response format for {self.hostname}")
            data = None   
        logger.debug(data)
        logger.debug(f"END:   http://{self.ip}/{endpoint}: --------------------->")
        return data

    def isDeviceOnline(self, dev):
        response = os.system(f"ping -c 1 -W 1 {dev} > /dev/null 2>&1")
        return response == 0
        
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
        DevList[netname]['devhandle'] = DevHandle(DevList[netname], f"{netname}.local")
        if DevList[netname]['devhandle'].isonline:
            for ep in DevList[netname]['eps']:
                DevList[netname][ep] = DevList[netname]['devhandle'].read(ep)
