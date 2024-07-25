###############################################################
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################
import logging 
import os
import socket
import json
import requests
import importlib

import config as cfg

logger = logging.getLogger(__name__)
logging.getLogger('urllib3').setLevel(logging.WARNING)

class DevHandler:
    def __init__(self, hostname, iBlock):
        try:
            self.iBlock = iBlock
            self.iBlock['ip'] = socket.gethostbyname(hostname)
            self.iBlock['hostname'] = hostname
            logger.debug(f"IP-Address for {hostname} is {self.iBlock['ip']}")
        except socket.gaierror as e:
            self.iBlock['isonline']= False            
            logger.error(f"{hostname}: {e}")
        else:
            self.iBlock['isonline'] = self.isDeviceOnline(self.iBlock['ip'])
            print(f"importiere: {self.iBlock['modul']}")
            self.iBlock['driver'] = importlib.import_module(self.iBlock['modul'])
            instance = self.iBlock['driver'].driver(self.iBlock)
        
    def read(self, endpoint):
        logger.debug(f"START: http://{self.iBlock['ip']}/{endpoint}: --------------------->")
        try:
            res = requests.get (f"http://{self.iBlock['ip']}/{endpoint}")
            if not res.ok:
                raise ValueError (f"endpoint was '{endpoint}'")
        except Exception as e:
            logger.error(f"cant get the Shelly data: {e}")
            return None
        if self.iBlock['format'] == "json":
            data = json.loads(res.text)
        elif self.iBlock['format'] == 'text':
            data = res.text
        else:
            logger.error(f"wrong response format for {self.iBlock['hostname']}")
            data = None   
        logger.debug(data)
        logger.debug(f"END:   http://{self.iBlock['ip']}/{endpoint}: --------------------->")
        return data

    def isDeviceOnline(self, dev):
        response = os.system(f"ping -c 1 -W 1 {dev} > /dev/null 2>&1")
        return response == 0
