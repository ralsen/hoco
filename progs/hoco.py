#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################
import time
import logging 
import os

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
    reg = registry(cfg)
    
    old_x = []

    try:
        while True:
            devices = devhandler.discover_devices()
            reg.save_registry(devices)
            x = cfg['ThreadManager'].get_all()
            if x != old_x:
                new_threads = set(x) - set(old_x)   # neu dazugekommen
                mis_threads = set(old_x) - set(x)    # weggefallen
                logger.info(f"{len(x)} active Threads:")
                logger.info(f"New thread(s):     {new_threads}")
                if mis_threads:
                    logger.info(f"Removed thread(s): {mis_threads}")
                logger.info(f"all thread(s):     {x}")
                old_x = x
            #time.sleep(cfg['mainloop_sleep'])
            time.sleep(5)
    except KeyboardInterrupt:
        reg.save_registry(devices)
        logging.info("CTRL+C pressed – terminate Threads…")
        cfg['ThreadManager'].stop_all()

