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
    def __init__(self, hostname: str, iBlock: dict):
        self.mBlock = {}
        try:
            self.iBlock = iBlock
            self.iBlock['hostname'] = hostname
            self.mBlock['ip'] = socket.gethostbyname(hostname)
            logger.debug(f"IP-Address for {hostname} is {self.mBlock['ip']}")
        except socket.gaierror as e:
            self.mBlock['ip]'] = None
            self.mBlock['isonline']= False            
            logger.error(f"{hostname}: {e}")
        else:
            self.mBlock['isonline'] = self.isDeviceOnline(self.mBlock['ip'])
            self.mBlock['modul'] = importlib.import_module(self.iBlock['modul'])
            self.mBlock['driver'] = self.mBlock['modul'].driver(self, self.iBlock, self.mBlock)
            
    def read(self, endpoint: str):
        logger.debug(f"START: http://{self.mBlock['ip']}/{endpoint}: --------------------->")
        try:
            res = requests.get (f"http://{self.mBlock['ip']}/{endpoint}")
            if not res.ok:
                raise ValueError (f"endpoint was '{endpoint}'")
        except Exception as e:
            errstr = f"cant get data from device '{self.iBlock['name']}' with {self.mBlock['ip']} ({e})"
            logger.error(errstr)
            return False, errstr
        if self.iBlock['format'] == "json":
            return True, json.loads(res.text)
        elif self.iBlock['format'] == 'text':
            return True, res.text
        else:
            errstr = f"wrong response format for {self.iBlock['hostname']}"
            logger.error(errstr)
            return False, errstr   

    def isDeviceOnline(self, dev: str) -> bool:
        response = os.system(f"ping -c 1 -W 1 {dev} > /dev/null 2>&1")
        return response == 0
