import time
import logging 
import threading
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
        while True:
            res, html = self.drv.read(self.iBlock['infoURL']) 
            if res == True:
                htmlDict = self.getHTML_Keys(html)
                logger.info(f"got htmlKey from {self.iBlock['name']}: {htmlDict['uptime']}")
            else:
                logger.error(f"{self.iBlock['name']}: {i} is offline!!")
            i+=1
            time.sleep(self.iBlock['time'])
    
    def getHTML_Keys(self, html: str) -> dict:
        data = {}
        data['uptime'] = 1234567890
        return data

    def test(self):
        logger.debug(f"!!! bin in Test() !!! {self}")
        