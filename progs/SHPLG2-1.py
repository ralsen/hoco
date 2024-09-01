import time
import logging 
import threading
import requests
import json
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class driver:
    def __init__(self, driver, iBlock, mBlock):
        self.iBlock = iBlock
        self.mBlock = mBlock
        self.drv = driver
        threading.Thread(target=self._monitoring_thread, daemon=True).start()    
        logger.info(f"driver '{self.iBlock['modul']}' installed for {self.iBlock['name']}")        
        self.test()
        
    def _monitoring_thread(self):
        i = 0
        ison = False
        while True:
            res, html = self.drv.read(self.iBlock['infoURL']) 
            if res == True:
                ison = True
                htmlDict = self.getHTML_Keys(html)
                logger.info(f"got Solar-Power from {self.iBlock['name']}: {htmlDict['power']}")
            else:
                if ison:
                    logger.error(f"{self.iBlock['name']}: is offline!!! counter: {i}")
                    ison = False
            i+=1
            time.sleep(self.iBlock['time'])
    
    def getHTML_Keys(self, html: str) -> dict:
        logger.debug(html)
        data = {}
        try:
            res = requests.get (f"http://{self.mBlock['ip']}/meter/0.local")
        except Exception as e:
            logger.error(f"cant get the data  from {self.iBlock['name']}: {e}")        
        data = json.loads(res.text)
        data['uptime'] = 22222
        return data

    def test(self):
        logger.debug(f"!!! bin in Test() !!! {self}")