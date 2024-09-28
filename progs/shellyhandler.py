#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################
import logging 
import socket
import requests
import time
import yaml
import threading
from zeroconf import ServiceBrowser, Zeroconf

import config as cfg

logger = logging.getLogger(__name__)
logging.getLogger('urllib3').setLevel(logging.WARNING)

class ShellyHandler:
    def __init__(self):
        with open(f"{cfg.ini['YMLPath']}/devs.yml", 'r') as ymlfile:
            self.DevList = yaml.safe_load(ymlfile)
        cfg.ini['DevList'] = self.DevList
        logger.debug(cfg.ini['DevList'])
        
    def discover_shelly_devices(self, DevList, timeout=5):
        """Durchsucht das lokale Netzwerk nach Shelly-Geräten."""
        zeroconf = Zeroconf()
        listener = ShellyListener()
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
                this['hostname'] = full_name.split('.')[0]
                this['ip'] = ip
                this['devdef'] = self.DevList.get(this['hostname'], None)
                if this['devdef'] is not None:
                    logger.debug(f"checking device protocol: {this['devdef']['name']} (IP: {ip})")
                    this['protocol'] = self.check_protocol(ip, this['devdef']['name'])
                    logger.debug(f"Protocol for {this['devdef']['name']} is {this['protocol']}")
                    knownDevices += 1
                else:
                    logger.error(f"unknown entry for {this['hostname']}")
                    this['protocol'] = "unknown"
                    unknownDevices += 1
                this['service'] = Service(this)
        
        logger.info(f"got {knownDevices} of {len(listener.devices)} devices with {knownDevices} known protocols. Please check the {unknownDevices} unrecognised devices in {cfg.ini['YMLPath']}/devs.yml")
        return allDevice, knownDevices, unknownDevices

    def check_protocol(self, device_ip, device_name):
        """Ermittelt, welches Protokoll das Shelly-Gerät verwendet."""
        logger.debug(f"Prüfe das Protokoll für Gerät: {device_name} (IP: {device_ip})")
        
        http_url = f"http://{device_ip}/status"
        rpc_url = f"http://{device_ip}/rpc/Shelly.GetStatus"

        try:
            # Teste HTTP/CoAP (Gen 1)
            http_response = requests.get(http_url, timeout=5)
            if http_response.status_code == 200:
                return "HTTP/CoAP (Gen 1)"
        except requests.exceptions.RequestException:
            pass

        try:
            # Teste RPC (Gen 2)
            rpc_response = requests.get(rpc_url, timeout=5)
            if rpc_response.status_code == 200:
                return "RPC (Gen 2)"
        except requests.exceptions.RequestException:
            pass
        
        return "Unbekanntes Protokoll"

class ShellyListener:
    """Listener für Shelly-Geräte, um IP-Adressen zu sammeln."""
    def __init__(self):
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
        self.my = this
        threading.Thread(target=self._monitoring_thread, daemon=True).start()
        pass
    
    def _monitoring_thread(self):
        while True:
            if self.my['protocol'] != 'unknown' and self.my['devdef'] != None:
                logger.debug(self.read())
                time.sleep(self.my['devdef']['time'])
            else:
                time.sleep(10)

    def read(self):
        logger.debug(f"---> reading from device {self.my['devdef']['name']} ###{self.my['devdef']['infoURL']} ")
        max_retries = self.my['devdef'].get('retry', 1)  # Standardmäßig 1 Versuch, falls 'retry' nicht gesetzt ist
        result = {}
        if self.my['ip'] == None:
            return result        
        for endpoint in self.my['devdef']['infoURL']:
            for retry in range(max_retries):
                logger.debug(f"retry {retry + 1} for device {self.my['devdef']['name']}")
                try:
                    logger.debug(f"Request from: {self.my['devdef']['name']} on http://{self.my['ip']}/{endpoint}")
                    res = requests.get(f"http://{self.my['ip']}/{endpoint}")
                    logger.debug(f"OJE --- {res}")
                    if res.ok:
                        result[endpoint] = res.text                    
                        break  # Erfolgreiche Anfrage, Schleife verlassen
                    else:
                        raise ValueError(f"endpoint was '{endpoint}'")
                except Exception as e:
                    logger.warning(f"Retry {retry + 1} failed: {e}")
                    result = f"cant get data from device '{self.my['devdef']['name']}' with {self.my['ip']} ({e})"
                    logger.error(result)
            logger.debug(f"needed {retry + 1} of {max_retries} retries.")
        logger.debug(f"---> reading done from device {self.my['devdef']['name']}")
        return result
            