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
            res = self.my['devhd'].read() 
            if res != None:
                ison = True
                htmlDict = self.getHTML_Keys(res)
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
                attempt = 0
                max_retries = self.my.get('retry', 1)
                while attempt < max_retries:
                    try:
                        logger.debug(f"try to reach server: {attempt}")
                        response = requests.post(f"http://{self.my['ServerName']}.local:{self.my['ServerPort']}", json=data)
                        break
                    except Exception as e:
                        attempt += 1
                        if attempt == max_retries:
                            logger.error(f"could not send to server http://{self.my['ServerName']}.local:{self.my['ServerPort']} (after {max_retries} retries)")
                logger.debug(f"Answer: {response.text}")                
            else:
                if ison:
                    logger.error(f"{self.my['hostname']}: is offline!!! counter: {i}")
                    ison = False
            i+=1
            time.sleep(self.my['time'])
    
    def getHTML_Keys(self, keys: str) -> dict:
        #logger.debug(html)
        data = {}
        data = json.loads(keys[0])
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