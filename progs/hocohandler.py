
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################
import logging 
import socket
import requests
import time
import yaml
import threading
import json
from zeroconf import ServiceBrowser, Zeroconf
from dispatcher import Dispatcher

import config as cfg

logger = logging.getLogger(__name__)
logging.getLogger('urllib3').setLevel(logging.WARNING)

class DeviceHandler:
    def __init__(self, cfg):
        self.cfg = cfg
        with open(f"{self.cfg['YMLPath']}/{self.cfg['Devices']}", 'r') as ymlfile:
            self.DevList = yaml.safe_load(ymlfile)
        logger.debug(self.DevList)
        
    def discover_devices(self, timeout=5):
        """Durchsucht das lokale Netzwerk nach Geräten."""
        zeroconf = Zeroconf()
        listener = DeviceListener(self.DevList)
        browser = ServiceBrowser(zeroconf, "_http._tcp.local.", listener)
        # Warte einige Sekunden, um Geräte zu finden
        time.sleep(timeout)
        zeroconf.close()
        return self.initDevices(listener)
    
    def initDevices(self, listener):
        knownDevices = 0
        unknownDevices = 0
        allDevices = {}
        
        if not listener.devices:
            logger.error("No devices found.")
        else:
            for full_name in listener.devices:
                logger.debug(f"Processing device: {full_name}")
                allDevices[full_name] = {}
                this = allDevices[full_name]
                this['FullName'] = full_name
                this['Hostname'] = listener.devices[full_name]['info'].server.split('.')[0]  # Hostname extrahieren
                try:
                    device = self.DevList[this['Hostname']]
                except KeyError:
                    logger.warning(f"Device {this['Hostname']} not found in devs.yml. Please add it to the yml file.")
                    unknownDevices += 1
                    continue
                this['IP'] = listener.devices[full_name]['IP']
                this['Type'] = device['Type']
                this['Template'] = self.DevList[device['Type']]
                this['Protocol'] = this['Template']['Protocol']
                this['Cycle'] = device['Cycle']
                this['Hardware'] = this['Template']['Hardware']
                this['InfoURL'] = this['Template']['InfoURL']
                this['ServerPort'] = device['ServerPort']
                this['ServerName'] = device['ServerName']
                this['Retry'] = device['Retry']
                logger.debug(f"Protocol is {this['Protocol']}")
                knownDevices += 1
                this['service'] = Service(self.cfg, this)
                logger.debug(f"device: '{this['Hostname']}' is defined")
                
        logger.info(f"got {knownDevices} of {len(listener.devices)} devices with {knownDevices} known protocols. Please check the {unknownDevices} unrecognised devices in {self.cfg['YMLPath']}/devs.yml")
        return allDevices, knownDevices, unknownDevices

class DeviceListener:
    """Listener für Shelly-Geräte, um IP-Adressen zu sammeln."""
    def __init__(self, DevList):
        self.DevList = DevList
        self.devices = {}

    def remove_service(self, zeroconf, type, name):
        # Entfernen von Diensten (nicht benötigt)
        pass

    def add_service(self, zeroconf, type, name):
        # Hinzufügen von Diensten
        info = zeroconf.get_service_info(type, name)
        ip_address = socket.inet_ntoa(info.addresses[0])
        self.devices[name] = ip_address
        self.devices[name] = {}
        self.devices[name]['IP'] = ip_address
        self.devices[name]['info'] = info
        self.devices[name]['zeroconf'] = zeroconf
        logger.info(f"found device: {name} with IP {ip_address}")

    def update_service(self, zeroconf, service_type, name):
        logger.info("### mDNS service updated: ### %s", name)
        pass
           
class Service:
    def __init__(self, cfg, this):
        self.this = this
        self.name = self.this['Hostname']
        self.cfg = cfg
        #threading.Thread(target=self._monitoring_thread, daemon=True).start()
        self.cfg['ThreadManager'].start(f"monitoring for {self.name}", target=self.__monitoring_thread__, args=())
        pass
    
    def __monitoring_thread__(self, stop_event: threading.Event):
        logger.debug(f"starting monitoring thread for {self.name}")
        
        while not stop_event.is_set():            
            logger.debug(f"calling {self.name} with protocol: {self.this['Protocol']}")
            if self.this['Protocol'] != 'unknown':
                try:
                    logger.debug(f"Monitor active: {self.name}")
                    devrsp = self.read()
                    self.this['last_response'] = time.time()
                except Exception as e:
                    logger.error(f"error response from: {self.name}: {e}")
                    pass
                try:
                    self.sendServer(devrsp)
                except Exception as e:
                    logger.error(f"error sending to server: {self.name}: {e}")
                    pass
            else:
                logger.error(f"unknown protocol for device {self.name}")
                stop_event.wait(120)
            if stop_event.wait(self.this['Cycle']):
                break            
        
    def sendServer(self, infos):
        #logger.info((infos))
        if self.this['Protocol'] == 'unknown':
            logger.error("unknown Protocol")
            return None
        if self.this['Protocol'] == 'Gen 1':
            logger.debug("Gen 1 protocol")
        elif self.this['Protocol'] == 'Gen 2':
            logger.debug("Gen 2 protocol")
        elif self.this['Protocol'] == 'ESP':
            logger.debug("ESP protocol")
        else:
            logger.error("wrong Protocol")
            return None

        #logger.debug(f"Sending: {infos}")
        attempt = 0
        max_retries = self.this.get('retry', 1)
        while attempt < max_retries:
            try:
                #infos.pop('name', None)  # entfernen, da nicht relevant
                logger.debug(f"try to reach server: {attempt}")
                #logger.debug(f"posting to: http://{self.this['ServerName']}.local:{self.this['ServerPort']} data: {json.dumps(infos)}")
                response = requests.post(f"http://{self.this['ServerName']}.local:{self.this['ServerPort']}", json=infos)
                logger.debug(f"getting: {response}")
                break
            except Exception as e:
                attempt += 1
                if attempt == max_retries:
                    logger.error(f"could not send to server http://{self.this['ServerName']}.local:{self.this['ServerPort']} (after {max_retries} retries)")
        logger.debug(f"Answer: {response.text}, {self.this['Hostname']}")                
        pass    

    def read(self):
        logger.debug(f"reading from device: {self.name} --- URL: {self.this['InfoURL']}")
        max_retries = self.this.get('Retry', 1)  # Standardmäßig 1 Versuch, falls 'retry' nicht gesetzt ist
        result = {}
        
        #Dispatcher.handle()
        #data = {"Type": f"{self.this['Type']}"+"2"}
        #d = Dispatcher(data)
        
        if self.this['IP'] is None:
            logger.error(f"{self.name}: no IP address found")
            return result   
        logger.debug(f"{self.name}: starting read with max_retries={max_retries}")     
        for retry in range(max_retries):
            #logger.debug(f"{self.name}: {self.this['InfoURL'][0]}")
            try:
                logger.debug(f"{self.name}: {retry + 1}. request on http://{self.this['IP']}/{self.this['InfoURL']}") 
                res = requests.get(f"http://{self.this['IP']}/{self.this['InfoURL']}", timeout=5)
                logger.debug(f"{self.name}: {res}")
                if res.ok:
                    dispatch_data = {
                        "Type": self.this['Type'],
                        "device": self.this,
                        "response": res,
                    }
                    data = Dispatcher(dispatch_data).handle()
                    result = data
                    break  # Erfolgreiche Anfrage, Schleife verlassen
                else:
                    raise ValueError(f"endpoint was we have no endpoint anymore")
            except Exception as e:
                logger.warning(f"{self.name}: Retry {retry + 1} failed: {e}")
                result = f"{self.name}: cant get data from device with {self.this['IP']} ({e})"
                logger.error(result)
        logger.debug(f"{self.name}: needed {retry + 1} of {max_retries} retries.")
        logger.debug(f"---> {self.name}: reading done: {result}")
        return result
            
"""
posting to: http://Server64.local:8080 data: {"Version": "V5.0f", "Hostname": "Buero-68C63A87FACE", "Type": "DS1820", "Hardw": "NODEMCU", "Chip-ID": "0x87face", "MAC-Address": "68:C6:3A:87:FA:CE", "Network": "janzneu", "Network-IP": "192.168.2.38", "Devicename": "Buero", "AP-Name": "ESPnet", "cfg-Size": "0x14c", "Hash": "0x8ffc96", "Display": "False", "uptime": "65 days - 4 hours - 1 minutes - 4 seconds", "Measuring cycle": "150 s (remainig: 24 s)", "Transmit cycle": "300 s (remaining: 20 s)", "PageReload cycle": "10 s", "Server": "192.168.2.5", "Port": "8080", "LED": "on", "Signal strength": "-77", "good Transmissions": "18761", "bad Transmissions": "7", "Pages delivered": "617", "Measurements": "37288"}
"""