#!/usr/bin/env python3 xxx
# -*- coding: utf-8 -*-
import logging
import yaml
import os

logger = logging.getLogger(__name__)

def init(ProgName):
    global ini

    ini = {}
    current_dir = os.getcwd()
    print(current_dir)
    current_dir += ''
    with open(f'{current_dir}/yml/config.yml', 'r') as ymlfile:
        yml = yaml.safe_load(ymlfile)

    RootPath = current_dir #yml['ROOT_PATH']
    ini['LogPath'] = RootPath + yml['pathes']['LOG']
    ini['DataPath'] = RootPath + yml['pathes']['DATA']
    ini['RRDPath'] = RootPath + yml['pathes']['RRD']
    ini['YMLPath'] = RootPath + yml['pathes']['YML']
    ini['PNGPath'] = RootPath + yml['pathes']['PNG']
    ini['DaboServerName'] = yml['Communication']['DaboServerName']
    ini['DaboServerPort'] = yml['Communication']['DaboServerPort']
    ini['debugdatefmt'] = yml['debug']['datefmt']
    ini['logSuffix'] = yml['suffixes']['log']
    ini['dataSuffix'] = yml['suffixes']['data']
    ini['hirestime'] = yml['debug']['hirestime']
    ini['humanTimestamp'] = yml['debug']['humanTimestamp']
    ini['Mailing'] = yml['debug']['Mailing']

#    ini['Dstore'] = ds.DS(f"{ini['YMLPath']}/{yml['files']['DATASTORE_YML']}") ######
