import time
import logging 
import threading
from bs4 import BeautifulSoup
import pandas

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
            on = self.drv.isDeviceOnline(self.mBlock['ip'])
            if on:
                res, html = self.drv.read(self.iBlock['infoURL']) 
                if res == True:
                    htmlDict = self.getHTML_Keys(html)
                    logger.debug(f"got htmlKeys -> {htmlDict['uptime']}")
            else:
                logger.error(f"{self.iBlock['hostname']}: {i} is offline!!")
            #html2 = self.drv.read('status')
            #htmlDict = self.getHTML_Keys(html2)
            i+=1
            time.sleep(self.iBlock['time'])
    
    def getHTML_Keys(self, html: str) -> dict:
        soup = BeautifulSoup(html, 'html.parser')
        # Finden aller relevanten Elemente (z.B. <p> tags innerhalb eines div mit class 'info')
        info_div = soup.find('div1')
        text_lines = info_div.get_text(separator='\n').split('\n')

        data = {}

        for line in text_lines:
            if ':' in line:
                key, value = line.split(':', 1)
                data[key.strip()] = value.strip()
        return data

    def test(self):
        logger.debug(f"!!! bin in Test() !!! {self}")