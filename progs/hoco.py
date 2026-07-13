#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################
import time
import logging 
import os
import json
import requests

import config as config
import hocohandler as dh
from registry import registry
from dispatcher import Dispatcher, load_handlers

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    current_file_path = os.path.realpath(__file__)
    current_file_name = os.path.basename(current_file_path)

    cfg = config.InitManager(current_file_name).ini

    logger.info("")
    logger.info(f'---------- Starte {current_file_path} ----------') 

    load_handlers()

    logger.debug("Searching Devices ...")
    devhandler = dh.DeviceHandler(cfg)
    devices = devhandler.discover_devices()
    reg = registry(cfg)
    
    # ganz wichtig: einmal aufrufen
    #data = {"Type": "SNSW-001X16EU"}
    #d = Dispatcher(data)
    #cfg['dispatchers'] = d
    #logger.debug(f"Handling device: {d.handle()}")

    old_x = []
    i = 0
    try:
        while True:
            logger.info(f"Mainloop iteration: {i}")
            i += 1
            x = cfg['ThreadManager'].get_all()
            if x == old_x:
                logger.info(f"{len(x)} active threads. No changes.")
            else:
                new_threads = set(x) - set(old_x)   # neu dazugekommen
                mis_threads = set(old_x) - set(x)    # weggefallen
                logger.info(f"{len(x)} active Threads:")
                logger.info(f"New thread(s):     {new_threads}")
                if mis_threads:
                    logger.info(f"Removed thread(s): {mis_threads}")
                logger.info(f"all thread(s):     {x}")
                old_x = x
            #if i == 5:
                #logger.info("terminating")
                #cfg['ThreadManager'].stop_all()
                #os._exit(0)
            time.sleep(cfg['mainloop_sleep'])
            logger.info("Mainloop cycle done.")
    except KeyboardInterrupt:
        reg.save_registry(devices[0])
        logging.info("CTRL+C pressed – terminate Threads…")
        cfg['ThreadManager'].stop_all()

