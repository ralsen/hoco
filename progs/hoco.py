###############################################################
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################
import datetime
import logging 
import os
import socket
import yaml
import json
import requests

import config as cfg

logger = logging.getLogger(__name__)
logging.getLogger('urllib3').setLevel(logging.WARNING)

def getOnlineDevices():
    devlist = []
    for i in range (1, 140):
        print(i)
        url = f"http://192.168.2.{i}"  # Beispiel-URL des Geräts
        try:
            response = requests.get(url, timeout=1)
            if response.status_code == 200:
                devlist.append(f"http://192.168.2.{i}")
        except:
            pass
    return devlist

def isDeviceOnline(dev):
    response = os.system(f"ping -c 1 -W 1 {dev}.local > /dev/null 2>&1")
    return response == 0

class Shelly:
    def __init__(self, name, ip):
        self.ip = ip
        self.name = name
        
    def read(self, endpoint):
        print(self.ip)
        try:
            res = requests.get (f"http://{self.ip}/{endpoint}")
        except Exception as e:
            logger.error(f"cant get the Shelly data: {e}")
            return None
        data = json.loads(res.text)
        logger.info(f"START: {self.name} - {endpoint}: --------------------->")
        logger.info(data)
        logger.info(f"END:   {self.name} - {endpoint}: --------------------->")
        return data
        
if __name__ == '__main__':
    current_file_path = os.path.realpath(__file__)
    current_file_name = os.path.basename(current_file_path)

    cfg.init(current_file_name)
    x = datetime.datetime.now()

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s :: %(levelname)-7s :: [%(name)+15s] [%(lineno)+3s] :: %(message)s',
        datefmt=cfg.ini['debugdatefmt'],
        handlers=[
            logging.FileHandler(f"{cfg.ini['LogPath']}/{current_file_name[:-3]}_{socket.gethostname()+x.strftime(cfg.ini['logSuffix'])}.log"),
            logging.StreamHandler()
        ])

    logger.info("")
    logger.info(f'---------- starting {current_file_path} ----------') 

    ServerName = cfg.ini['DaboServerName']
    ServerPort = cfg.ini['DaboServerPort']
    #server = HTTPServer((ServerName, ServerPort), webserverHandler)
    logger.info(f"Device server started on {socket.getfqdn()}")
    
    with open(f"{cfg.ini['YMLPath']}/devs.yml", 'r') as ymlfile:
        DevList = yaml.safe_load(ymlfile)
    logger.info(DevList)
    
    for netname in DevList:
        if isDeviceOnline(netname):
            print(f"{netname} is online")
        else:
            print(f"{netname} is offline")
    #print(getOnlineDevices())
    for key, value in DevList.items():
        devdict = {key: value}
        logger.info(f"Hardware: {devdict[key]['Hardware']} - Type: {devdict[key]['Type']}")
        logger.info(devdict)
        logger.info("")
    """
    GartenLampe = Shelly('Gartenlampe', '192.168.2.139')
    data = GartenLampe.read("rpc/Shelly.GetComponents")
    for key in data['components']:
        print(key)
        ssid = key.get('config', {}).get('ap', {}).get('ssid', 'N/A')
        sta_ip = key.get('status', {}).get('sta_ip', 'N/A')
        rssi = key.get('status', {}).get('rssi', 'N/A')
        
        print(f"IP:   {sta_ip}")
        print(f"RSSI: {rssi}")
        print(f"SSID: {ssid}")    #print(data['components'])

    
    data = GartenLampe.read("rpc/Shelly.GetStatus")
    data = GartenLampe.read("rpc/Shelly.GetConfig")
    data = GartenLampe.read("rpc/Shelly.GetDeviceInfo")
    data = GartenLampe.read("rpc/Sys.GetStatus")
    data = GartenLampe.read("rpc/Sys.GetConfig")
    data = GartenLampe.read("rpc/Wifi.GetStatus")
    data = GartenLampe.read("rpc/Wifi.GetConfig")
    data = GartenLampe.read("rpc/Eth.GetStatus")
    data = GartenLampe.read("rpc/Eth.GetConfig")
    data = GartenLampe.read("rpc/BLE.GetStatus")
    data = GartenLampe.read("rpc/BLE.GetConfig")
    data = GartenLampe.read("rpc/Cloud.GetStatus")
    data = GartenLampe.read("rpc/Cloud.GetConfig")
    data = GartenLampe.read("rpc/Ws.GetStatus")
    data = GartenLampe.read("rpc/Ws.GetConfig")

    Solar = Shelly('Solar', '192.168.2.136')
    data = Solar.read("settings")
    data = Solar.read("status")
    data = Solar.read("relay/0")    
    data = Solar.read("meter/0")        
    """