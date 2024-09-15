import time
import logging 
import threading
import requests
import json
#from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class driver:
    def __init__(self, my: dict):
        self.my = my
        self.my['drv'] = driver
        threading.Thread(target=self._monitoring_thread, daemon=True).start()    
        logger.info(f"driver '{self.my['modul']}' installed for {self.my['hostname']}")        
        self.test()
        
    def _monitoring_thread(self):
        i = 0
        ison = False
        while True:
            res, html = self.my['devhd'].read(self.my['infoURL']) 
            if res == True:
                ison = True
                htmlDict = self.getHTML_Keys(html)
                logger.debug(f"got Solar-Power from {self.my['hostname']}: {htmlDict['power']}")
                data = {self.my['hostname']: {}}
                #data[self.hostname]['Power'] = htmlDict['power']
                #ds.handle_DataSet(data)
                
            else:
                if ison:
                    logger.error(f"{self.my['hostname']}: is offline!!! counter: {i}")
                    ison = False
            i+=1
            time.sleep(self.my['time'])
    
    def getHTML_Keys(self, html: str) -> dict:
        #logger.debug(html)
        data = {}
        try:
            res = requests.get (f"http://{self.my['ip']}/meter/0.local")
        except Exception as e:
            logger.error(f"cant get the data  from {self.my['hostname']}: {e}")        
        data = json.loads(res.text)
        data['uptime'] = 22222
        return data

    def test(self):
        logger.debug(f"!!! bin in Test() !!! {self}")