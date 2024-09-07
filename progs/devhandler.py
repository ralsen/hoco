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
    def __init__(self, name: str, dl: dict):
        self.my = dl
        self.my['hostname'] = name
        self.my['ip'] = None
        self.my['isonline'] = False
        try:
            self.my['ip'] = self.regDevice(name)
        except socket.gaierror as e:
            self.my['ip]'] = None
            self.my['isonline']= False            
            logger.error(f"{hostname}: {self.my['ip']} - {e}")
        finally:
            self.my['modul'] = importlib.import_module(self.my['modul'])
            self.my['driver'] = self.my['modul'].driver(self.my)

    def regDevice (self, hostname):
        self.my['ip'] = None
        self.my['isonline'] = False
        try:
            self.my['ip'] = socket.gethostbyname(f"{hostname}.local")
            self.my['isonline'] = True
            logger.debug(f"IP-Address for {hostname} is {self.my['ip']}")
        except socket.gaierror as e:
            self.my['ip'] = None
            self.my['isonline']= False            
            logger.error(f"{hostname}: {self.my['ip']} - {e}")
        return self.my['ip']
    
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
