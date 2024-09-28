#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################
import socket
import time
import yaml
import datetime
import logging 
import os

import config as cfg
import shellyhandler as sh

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    current_file_path = os.path.realpath(__file__)
    current_file_name = os.path.basename(current_file_path)

    cfg.init(current_file_name)
    x = datetime.datetime.now()

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s :: %(levelname)-7s :: [%(name)+16s] [%(lineno)+3s] :: %(message)s',
        datefmt=cfg.ini['debugdatefmt'],
        handlers=[
            logging.FileHandler(f"{cfg.ini['LogPath']}/{current_file_name[:-3]}_{socket.gethostname()+x.strftime(cfg.ini['logSuffix'])}.log"),
            logging.StreamHandler()
        ])

    logger.info("")
    logger.info(f'---------- Starte {current_file_path} ----------') 

    ServerName = cfg.ini['DaboServerName']
    ServerPort = cfg.ini['DaboServerPort']
    logger.info(f"Geräteserver gestartet auf {socket.getfqdn()}")
    
    logger.debug("Searching Shelly-Devices ...")
    dh = sh.ShellyHandler()
    devices = dh.discover_shelly_devices(cfg.ini['DevList'])
    print("fertich")
    while True:
        logger.debug("sleeping...")
        time.sleep(10)