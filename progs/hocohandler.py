
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

import config as cfg

logger = logging.getLogger(__name__)
logging.getLogger('urllib3').setLevel(logging.WARNING)

class ShellyHandler:
    def __init__(self):
        with open(f"{cfg.ini['YMLPath']}/devs.yml", 'r') as ymlfile:
            self.DevList = yaml.safe_load(ymlfile)
        logger.debug(self.DevList)
        
    def discover_shelly_devices(self, timeout=5):
        """Durchsucht das lokale Netzwerk nach Shelly-Geräten."""
        zeroconf = Zeroconf()
        listener = ShellyListener(self.DevList)
        browser = ServiceBrowser(zeroconf, "_http._tcp.local.", listener)
        # Warte einige Sekunden, um Geräte zu finden
        time.sleep(timeout)
        zeroconf.close()
        return self.initDevices(listener)
    
    def initDevices(self, listener):
        knownDevices = 0
        unknownDevices = 0
        allDevice = {}
        
        if not listener.devices:
            logger.error("No Shelly Devices found.")
        else:
            for full_name, ip in listener.devices.items():
                allDevice[full_name] = {}
                this = allDevice[full_name]
                this['FullName'] = full_name
                this['Hostname'] = full_name.split('.')[0]
                device = self.DevList[this['Hostname']]
                this['IP'] = ip
                this['Type'] = self.DevList[device['Type']]
                
                this['Protocol'] = this['Type']['Protocol']
                this['Cycle'] = device['Cycle']
                this['Hardware'] = this['Type']['Hardware']
                this['InfoURL'] = this['Type']['InfoURL']
                this['ServerPort'] = device['ServerPort']
                this['ServerName'] = device['ServerName']
                this['Retry'] = device['Retry']
                logger.debug(f"Protocol is {this['Protocol']}")
                knownDevices += 1
                this['service'] = Service(this)
        
        logger.info(f"got {knownDevices} of {len(listener.devices)} devices with {knownDevices} known protocols. Please check the {unknownDevices} unrecognised devices in {cfg.ini['YMLPath']}/devs.yml")
        return allDevice, knownDevices, unknownDevices

class ShellyListener:
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
        if info and "shelly" in name.lower():
            ip_address = socket.inet_ntoa(info.addresses[0])
            self.devices[name] = ip_address
            logger.info(f"Gefundenes Shelly-Gerät: {name} mit IP {ip_address}")
            
class Service:
    def __init__(self, this):
        self.this = this
        self.name = self.this['Hostname']
        threading.Thread(target=self._monitoring_thread, daemon=True).start()
        pass
    
    def _monitoring_thread(self):
        while True:
            
            print(f"{self.this['Protocol']} mit {self.name}")
            if self.this['Protocol'] != 'unknown':
                print("eigentlich gehts")
                try:
                    devrsp = self.read()
                    logger.debug(f"{self.name}: {devrsp}")
                    self.sendServer(devrsp)
                except:
                    pass
                time.sleep(self.this['Cycle'])
            else:
                logger.debug(f"{self.name}: Monitor sleeps")
                time.sleep(10)

    def sendServer(self, infos):
        print()
        print((infos))
        if self.this['Protocol'] == 'unknown':
            return None
        if self.this['Protocol'] == 'Gen 1':
            test = json.loads(infos['meter/0'])
            power = test['power']
            test = json.loads(infos['settings'])
            Type = test['device']['type']
        if self.this['Protocol'] == 'Gen 2':
            return None

        data = {
            'name': self.this['Hostname'],
            'Type': Type,
            'IP': self.this['ip'],
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
                response = requests.post(f"http://{self.this['ServerName']}.local:{self.this['ServerPort']}", json=data)
                break
            except Exception as e:
                attempt += 1
                if attempt == max_retries:
                    logger.error(f"could not send to server http://{self.this['ServerName']}.local:{self.this['ServerPort']} (after {max_retries} retries)")
        logger.debug(f"Answer: {response.text}")                
            

    def read(self):
        logger.debug(f"---> {self.name}: reading from device URLs: {self.this['InfoURL']})")
        max_retries = self.this.get('Retry', 1)  # Standardmäßig 1 Versuch, falls 'retry' nicht gesetzt ist
        result = {}
        if self.this['IP'] is None:
            return result        
        for retry in range(max_retries):
            print(self.this['InfoURL']['power'])
            try:
                logger.debug(f"{self.name}: {retry + 1}. request on http://{self.this['IP']}/{self.this['InfoURL']['power']}") 
                res = requests.get(f"http://{self.this['IP']}/{self.this['InfoURL']['power']}") 
                logger.debug(f"{self.name}: {res}")
                if res.ok:
                    data = json.loads(res.text)
                    result = data['power']                    
                    break  # Erfolgreiche Anfrage, Schleife verlassen
                else:
                    raise ValueError(f"endpoint was we have no endpoint anymore")
            except Exception as e:
                logger.warning(f"{self.name}:Retry {retry + 1} failed: {e}")
                result = f"{self.name}: cant get data from device with {self.this['IP']} ({e})"
                logger.error(result)
        logger.debug(f"{self.name}: needed {retry + 1} of {max_retries} retries.")
        logger.debug(f"---> {self.name}: reading done")
        return result
            