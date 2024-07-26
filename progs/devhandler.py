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
        self.mBlock = {}
        try:
            self.iBlock = iBlock
            self.iBlock['hostname'] = hostname
            self.mBlock['ip'] = '11111111' #socket.gethostbyname(hostname)
            logger.debug(f"IP-Address for {hostname} is {self.mBlock['ip']}")
        except socket.gaierror as e:
            self.mBlock['ip]'] = None
            self.mBlock['isonline']= False            
            logger.error(f"{hostname}: {e}")
        else:
            self.mBlock['isonline'] = self.isDeviceOnline(self.mBlock['ip'])
            print(f"import: {self.iBlock['modul']}")
            self.mBlock['driver'] = importlib.import_module(self.iBlock['modul'])
            instance = self.mBlock['driver'].driver(self, self.iBlock, self.mBlock)
            print("installed")
    def read(self, endpoint):
        logger.debug(f"START: http://{self.mBlock['ip']}/{endpoint}: --------------------->")
        try:
            res = requests.get (f"http://{self.mBlock['ip']}/{endpoint}")
            if not res.ok:
                raise ValueError (f"endpoint was '{endpoint}'")
        except Exception as e:
            logger.error(f"cant get data from device '{self.iBlock['name']}' with {self.mBlock['ip']} ({e})")
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
        return True
        response = os.system(f"ping -c 1 -W 1 {dev} > /dev/null 2>&1")
        return response == 0
