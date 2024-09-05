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
import DataStore as ds

logger = logging.getLogger(__name__)
logging.getLogger('urllib3').setLevel(logging.WARNING)

class DevHandler:
    def __init__(self, hostname: str):
        #print(ds.DS.ds[hostname])
        self.hostname = hostname
        self.devdata = ds.DS.ds[self.hostname]['Commons']['devdata']
        self.devcoms = ds.DS.ds[self.hostname]['Commons'] # for debug watching
        self.devroot = ds.DS.ds[self.hostname]
        self.devdata['hostname'] = hostname
        self.devcoms['Active'] = False
        self.regDevice()
        self.devdata['modul'] = importlib.import_module(self.devdata['Modul'])
        self.devdata['driver'] = self.devdata['modul'].driver(self, self.hostname)
        self.devdata['handler'] = DevHandler
        print("fertich")
        
    def regDevice (self):
        self.devcoms['Active'] = False
        try:
            self.devdata['IP'] = socket.gethostbyname(self.hostname)
            self.devcoms['Active'] = True
            logger.debug(f"IP-Address for {self.hostname} is {self.devdata['IP']}")
        except socket.gaierror as e:
            self.devdata['IP'] = None
            self.devcoms['Active']= False            
            logger.error(f"{self.hostname}: {self.devdata['IP']} - {e}")
        return 
    
    def read(self, endpoint: str):
        logger.debug(f"START: Device: on http://{self.hostname}/{endpoint}: --------------------->")
        success = False
        result = None
        max_retries = self.devdata.get('Retry', 1)  # Standardmäßig 1 Versuch, falls 'retry' nicht gesetzt ist
        if self.devdata['IP'] == None:
            self.regDevice()
            if self.devdata['IP'] == None:
                return success, result        
        
        for attempt in range(max_retries):
            logger.debug(f"request info from http://{self.devdata['IP']}/{endpoint}")
            try:
                res = requests.get(f"http://{self.devdata['IP']}/{endpoint}")
                if res.ok:
                    if self.devdata['Format'] == "json":
                        result = json.loads(res.text)
                        success = True
                    elif self.devdata['Format'] == 'text':
                        result = res.text
                        success = True
                    else:
                        result = f"wrong response format for {self.hostname}"
                        logger.error(result)
                    break  # Erfolgreiche Anfrage, Schleife verlassen
                else:
                    raise ValueError(f"endpoint was '{endpoint}'")
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.warning(f"Attempt {attempt + 1} failed on device {self.hostname}: {e}")
                    logger.error(result)
        logger.debug(f"needed {attempt+1} of {max_retries} retries.")
        return success, result
            
    def isDeviceOnline(self, dev: str) -> bool:
        response = os.system(f"ping -c 1 -W 1 {dev} > /dev/null 2>&1")
        self.dBlock['isonline'] = response == 0
        return response == 0
