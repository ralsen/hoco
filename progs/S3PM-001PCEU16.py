import time
import logging 
import threading
import requests
import json
from bs4 import BeautifulSoup

import DataStore as ds

logger = logging.getLogger(__name__)

class driver:
    def __init__(self, driver, hostname: str):
        self.hostname = hostname
        self.devdata = ds.DS.ds[hostname]['Commons']['devdata']        
        self.drv = driver
        threading.Thread(target=self._monitoring_thread, daemon=True).start()    
        logger.info(f"driver '{self.devdata['Modul']}' installed for {hostname}")        
        self.test()
        
    def _monitoring_thread(self):
        i = 0
        ison = False
        while True:
            res, html = self.drv.read(self.devdata['InfoURL']) 
            if res == True:
                ison = True
                htmlDict = self.getHTML_Keys(html)
                logger.info(f"got uptime from {self.hostname}: {htmlDict['uptime']}")
            else:
                if ison:
                    logger.error(f"{self.hostname}: is offline!!! counter: {i}")
                    ison = False
            i+=1
            time.sleep(self.devdata['Time'])
    
    def getHTML_Keys(self, html: str) -> dict:
        logger.debug(html)
        data = {}
        data['uptime'] = 33333
        return data

    def test(self):
        logger.debug(f"!!! bin in Test() !!! {self}")