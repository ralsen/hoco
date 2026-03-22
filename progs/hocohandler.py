
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
        with open(f"{self.cfg['YMLPath']}/devs.yml", 'r') as ymlfile:
            self.DevList = yaml.safe_load(ymlfile)
        logger.debug(self.DevList)
        
    def discover_devices(self, timeout=5):
        """Durchsucht das lokale Netzwerk nach Geräten."""
        zeroconf = Zeroconf()
        listener = DeviceListener(self.DevList)
        browser = ServiceBrowser(zeroconf, "_http._tcp.local.", listener)
        print(browser)
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
            for full_name, ip in listener.devices.items():
                allDevices[full_name] = {}
                this = allDevices[full_name]
                this['FullName'] = full_name
                this['Hostname'] = full_name.split('.')[0]
                try:
                    device = self.DevList[this['Hostname']]
                except KeyError:
                    logger.warning(f"Device {this['Hostname']} not found in devs.yml. Please add it to the yml file.")
                    unknownDevices += 1
                    continue
                this['IP'] = ip
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
        #if info and "shelly" in name.lower():
        ip_address = socket.inet_ntoa(info.addresses[0])
        self.devices[name] = ip_address
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
                self.read()
                try:
                    if self.name == "shellyplug-083A8DF437C7":
                        logger.debug(f"Monitor active: {self.name}")
                        devrsp = self.read()
                        self.this['last_response'] = time.time()
                        self.sendServer(devrsp)
                except Exception as e:
                    logger.error(f"error response from: {self.name}: {e}")
                    pass
            else:
                logger.error(f"unknown protocol for device {self.name}")
                stop_event.wait(120)
            if stop_event.wait(self.this['Cycle']):
                break            
        
    def sendServer(self, infos):
        logger.info((infos))
        if self.this['Protocol'] == 'unknown':
            logger.error("unknown Protocol")
            return None
        if self.this['Protocol'] == 'Gen 1':
            logger.debug("Gen 1 protocol")
            power = infos['power']
        elif self.this['Protocol'] == 'Gen 2':
            logger.debug("Gen 2 protocol")
            return None
        elif self.this['Protocol'] == 'Gen 4':
            logger.debug("Gen 4 protocol")
            return None
        else:
            logger.error("wrong Protocol")
            return None

        data = {
            'name': self.this['Hostname'],
            'Type': self.this['Type'],
            'IP': self.this['IP'],
            'Hardware': self.this['Hardware'],
            'Power': power
        }    
        logger.debug(f"Sending: {data}")
        #requests evtl. in eigenen Thread packen
        attempt = 0
        max_retries = self.this.get('retry', 1)
        while attempt < max_retries:
            try:
                logger.debug(f"try to reach server: {attempt}")
                logger.debug(f"posting to: http://{self.this['ServerName']}.local:{self.this['ServerPort']} data: {data}")
                response = requests.post(f"http://{self.this['ServerName']}.local:{self.this['ServerPort']}", json=data)
                logger.debug(f"getting: {response}")
                break
            except Exception as e:
                attempt += 1
                if attempt == max_retries:
                    logger.error(f"could not send to server http://{self.this['ServerName']}.local:{self.this['ServerPort']} (after {max_retries} retries)")
        logger.debug(f"Answer: {response.text}")                
            

    def read(self):
        logger.debug(f"reading from device: {self.name} --- URL: {self.this['InfoURL']})")
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
                res = requests.get(f"http://{self.this['IP']}/{self.this['InfoURL']}")
                logger.debug(f"{self.name}: {res}")
                if res.ok:
                    dispatch_data = {
                        "Type": self.this['Type'],
                        "device": self.this,
                        "response": res,
                    }
                    data = Dispatcher(dispatch_data).handle()
                    logger.debug(f"{self.name}: dispatcher returned: {data}")
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
            
