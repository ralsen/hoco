#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################
import logging 
import socket
import requests
import time
from zeroconf import ServiceBrowser, Zeroconf

import config as cfg

logger = logging.getLogger(__name__)
logging.getLogger('urllib3').setLevel(logging.WARNING)

class ShellyHandler:
    def __init__(self):
        pass        

    def discover_shelly_devices(self, DevList, timeout=5):
        """Durchsucht das lokale Netzwerk nach Shelly-Geräten."""
        zeroconf = Zeroconf()
        listener = ShellyListener()
        browser = ServiceBrowser(zeroconf, "_http._tcp.local.", listener)
        
        # Warte einige Sekunden, um Geräte zu finden
        time.sleep(timeout)
        zeroconf.close()

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
                this['devdef'] = DevList.get(this['hostname'], None)
                this['service'] = Service()
                if this['devdef'] is not None:
                    logger.debug(f"checking device protocol: {this['devdef']['name']} (IP: {ip}")
                    this['protocol'] = self.check_protocol(ip, this['devdef']['name'])
                    logger.debug(f"Protocol for {this['devdef']['name']} is {this['protocol']}")
                    knownDevices += 1
                else:
                    logger.error(f"unknown entry for {this['hostname']}")
                    this['protocol'] = "unknown"
                    unknownDevices += 1
        
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
    def __init__(self):
        pass