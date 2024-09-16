import time
import logging 
import threading
import requests
import json

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
                data = {
                    'name': self.my['hostname'],
                    'Type': self.my['Type'],
                    'IP': self.my['ip'],
                    'Hardware': self.my['Hardware'],
                    'Power': htmlDict['power']
                }
                logger.debug(f"Sending: {data}")
                #requests evtl. in eigenen Thread packen
                response = requests.post(f"http://{self.my['ServerName']}.local:{self.my['ServerPort']}", json=data)
                logger.debug(f"Answer: {response.text}")                
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
        """
        —> sending to: http://192.168.2.2:8080
        —> {„name“:“No-Name_8C_CE_4E_DE_B2_F0“,
        “IP“:“192.168.2.114“,
        “Version“:“5.0a“,
        “Hardware“:“NODEMCU“,
        “Network“:“janzneu“,
        “APName“:“ESPnet“,
        “MAC“:“8C:CE:4E:DE:B2:F0“,
        “TransmitCycle“:“150“,
        “MeasuringCycle“:“150“,
        “Hash“:“97f72f“,
        “Size“:“332“,
        “PageReload“:“10“,
        “Server“:“192.168.2.2“,
        “Port“:“8080“,
        “uptime“:“5“,
        “delivPages“:“0“,
        “goodTrans“:“0“,
        “badTrans“:“0“,
        “LED“:“1“,
        “WiFi“:“-59“,
        “Type“:“DS1820-2“,
        “Adress_0“:“0000000000000000“,
        “Value_0“:“-127.00“,
        “Adress_1“:“0000000000000000“,
        “Value_1“:“-127.00“}
        """ 