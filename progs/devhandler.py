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
        self.mBlock['ip'] = None
        self.mBlock['isonline'] = False
        try:
            self.iBlock = iBlock
            self.iBlock['hostname'] = hostname
            self.mBlock['ip'] = self.regDevice(hostname)
        except socket.gaierror as e:
            self.mBlock['ip]'] = None
            self.mBlock['isonline']= False            
            logger.error(f"{hostname}: {self.mBlock['ip']} - {e}")
        finally:
            self.mBlock['modul'] = importlib.import_module(self.iBlock['modul'])
            self.mBlock['driver'] = self.mBlock['modul'].driver(self, self.iBlock, self.mBlock)

    def regDevice (self, hostname):
        self.mBlock['ip'] = None
        self.mBlock['isonline'] = False
        try:
            self.mBlock['ip'] = socket.gethostbyname(hostname)
            self.mBlock['isonline'] = True
            logger.debug(f"IP-Address for {hostname} is {self.mBlock['ip']}")
        except socket.gaierror as e:
            self.mBlock['ip'] = None
            self.mBlock['isonline']= False            
            logger.error(f"{hostname}: {self.mBlock['ip']} - {e}")
        return self.mBlock['ip']
    
    def read(self, endpoint: str):
        logger.debug(f"START: Device: {self.iBlock['name']} on http://{self.mBlock['ip']}/{endpoint}: --------------------->")
        
        success = False
        result = None
        max_retries = self.iBlock.get('retry', 1)  # Standardmäßig 1 Versuch, falls 'retry' nicht gesetzt ist
        if self.mBlock['ip'] == None:
            self.regDevice(self.iBlock['hostname'])
            if self.mBlock['ip'] == None:
                return success, result        
        
        for attempt in range(max_retries):
            try:
                res = requests.get(f"http://{self.mBlock['ip']}/{endpoint}")
                if res.ok:
                    if self.iBlock['format'] == "json":
                        result = json.loads(res.text)
                        success = True
                    elif self.iBlock['format'] == 'text':
                        result = res.text
                        success = True
                    else:
                        result = f"wrong response format for {self.iBlock['hostname']}"
                        logger.error(result)
                    break  # Erfolgreiche Anfrage, Schleife verlassen
                else:
                    raise ValueError(f"endpoint was '{endpoint}'")
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.warning(f"Attempt {attempt + 1} failed: {e}")
                    result = f"cant get data from device '{self.iBlock['name']}' with {self.mBlock['ip']} ({e})"
                    logger.error(result)
        logger.debug(f"needed {attempt+1} of {max_retries} retries.")
        return success, result
            
    def isDeviceOnline(self, dev: str) -> bool:
        response = os.system(f"ping -c 1 -W 1 {dev} > /dev/null 2>&1")
        self.mBlock['isonline'] = response == 0
        return response == 0
