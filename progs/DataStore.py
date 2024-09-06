#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# test


import config as cfg
import logging
import time
import datetime
import threading
import os
import yaml
import mailit as mi

logger = logging.getLogger(__name__)

# The DS class is a Python class that reads store definitions from a YAML file and generates stores
# based on the templates provided.
class DS():
    ds = dict()
    def __init__(self, StoreDefs):
        """
        The function initializes a class instance with store definitions from a YAML file and
        generates stores based on the specified template.
        
        :param StoreDefs: The parameter `StoreDefs` is a string that represents the file path of the
        store definitions file
        """
        logger.info(f"using store definitions from: {StoreDefs}")
        with open(StoreDefs, 'r') as file:
            StoreYML = yaml.safe_load(file)
        self.Stores = StoreYML
        try:
            for Store, template in StoreYML['generate_stores'].items():
                DS.append(self, Store, template)
        except Exception:
            pass

    def append(self, Store: str, templateName: str):
        """
        The `append` function takes in a `Store` and `templateName` as arguments, builds a store using 
        the template, and initializes the store with certain values.
        
        :param Store: The `Store` parameter is a string that represents the name of the store where the
        template will be appended
        :type Store: str
        :param templateName: The parameter `templateName` is a string that represents the name of a
        template
        :type templateName: str
        """
        try:
            template = self.Stores['DataStores'][templateName]
        except Exception as err:
            logger.error(f"Template {err} not definied for device {Store}.")
            return
        logger.info(f'Building Store for: {Store} with template: {templateName}')
        self.ds[Store] = dict()
        for ShelfTag, x in template.items():
            self.ds[Store][ShelfTag] = dict()
            self.ds[Store][ShelfTag]['CURRENT_DATA'] = 0
            self.ds[Store][ShelfTag]["lastUPD"] = None                                                           
            try:
                for DataBox, Value in x.items():
                    self.ds[Store][ShelfTag][DataBox] = Value
            except Exception:
                pass
            if ShelfTag == 'Commons':       # initialize Commons
                self.ds[Store]['Commons']['header'] = 'time'
                self.ds[Store]['Commons']['Active'] = False
                self.ds[Store]['Commons']['Flag'] = False
                self.ds[Store]['Commons']['Counter'] = 0
                self.ds[Store]['Commons']['lastUPD'] = ''
                self.ds[Store]['Commons']['initTime'] = datetime.datetime.now()
            if ShelfTag != 'Commons':       # Commons are not part of the csv-header  
                try:
                    if x['CSV_MODE'] != 'NONE':
                        self.ds[Store]['Commons']['header'] += ',' + ShelfTag
                        self.ds[Store][ShelfTag]['CSV_MODE_DATA'] = 0
                except Exception:
                    pass
        self.ds[Store]['Commons']['Service'] = Service(Store) # start store handling
        logger.debug(self.ds[Store])

# The `Service` class is responsible for handling data, monitoring for timeouts, merging data from
# different sources, and writing data to a CSV file or a database.
class Service():
    MyName = ''
    def __init__(self, StoreName):
        """
        The function initializes an object with a given store name and starts a monitoring thread.
        
        :param StoreName: The parameter `StoreName` is used to initialize the `MyName` attribute of the
        class. It represents the name of the store
        """
        self.dabodict = {'__DaBo': {}}
        self.MyName = StoreName
        try:
            for index, mergeStr in enumerate(DS.ds[self.MyName]['Commons']['MERGE']):
                logger.info(f"   merge: {index} - {mergeStr}")
                threading.Thread(target=self._merge_thread, args=(mergeStr[0], index,),daemon=True).start()        
        except Exception as err:
            logger.info(f"no merge for store: {self.MyName}")
            pass    
        threading.Thread(target=self._monitoring_thread, daemon=True).start()        

    def _monitoring_thread(self):
        """
        The function `_monitoring_thread` continuously checks for data updates and performs a merge
        operation, and if a timeout occurs, it sets the `Active` flag to False and logs an error
        message.
        """
        logger.info(f'monitoring started for: {self.MyName}')
        while True:
            if(DS.ds[self.MyName]['Commons']['TIMEOUT']):
                DS.ds[self.MyName]['Commons']['TIMEOUT'] -= 1
                if(not DS.ds[self.MyName]['Commons']['TIMEOUT']):
                    DS.ds[self.MyName]['Commons']['Active'] = False
                    logger.error(f'Message missed: {self.MyName}')
                    mi.mailit(f'Message missed: {self.MyName}')
            time.sleep(1)

    def setCallBack(self, shelf, function):
        DS.ds[self.MyName][shelf]['CaBa_1'] = function
        logger.info(f'callBack for Shelf "{shelf}" in Store "{self.MyName}" is set.')
        
    def handle_DataSet(self, DataSet):
        """
        The function `handle_DataSet` processes a given `DataSet` by iterating over its keys and calling
        the `handleData` method for each key, while logging any exceptions that occur.
        
        :param DataSet: DataSet is a dictionary containing key-value pairs. Each key represents a data
        set, and the corresponding value is the data associated with that data set
        """
        if cfg.ini['humanTimestamp']:
            if cfg.ini['hirestime']:
                timeStamp = datetime.datetime.fromtimestamp(time.time()).strftime(('%d.%m.%Y %H:%M:%S.%f'))
            else:
                timeStamp = datetime.datetime.fromtimestamp(time.time()).strftime(('%d.%m.%Y %H:%M:%S'))
        else:
            if cfg.ini['hirestime']:
                timeStamp = str(time.time())
            else:
                timeStamp = str(int(time.time()))
        for key in DataSet.keys():
            self.handleData(DataSet[key], timeStamp)
            try:
                self.handleData(DataSet[key], timeStamp)
            except Exception as err:
                logger.error(f'receiving invalid DataSet: {key} - {type(err)}')

    def handle_CAN(self, msg):
        """
        The function `handle_CAN` decodes a CAN-Bus message using a DBC file and handles the decoded
        data.
        
        :param msg: The parameter `msg` is a CAN message object. It contains information about the
        received CAN message, such as the arbitration ID (msg.arbitration_id) and the data (msg.data) of
        the message
        :return: If an exception occurs during the decoding of the CAN message, the function will log an
        error message and return. Otherwise, it will call the `handleData` method with the decoded
        message and the timestamp as arguments.
        """
        try:
            decoded_DBC = cfg.ini['CAN_dbc'].decode_message(msg.arbitration_id, msg.data)
        except Exception as err:
            logger.error(f'receiving unknown CAN-Bus message-ID: {str(msg.arbitration_id)} -> {err}')
            return
        if cfg.ini['humanTimestamp']:
            if cfg.ini['hirestime']:
                timeStamp = datetime.datetime.fromtimestamp(msg.timestamp).strftime(('%d.%m.%Y %H:%M:%S.%f'))
            else:
                timeStamp = datetime.datetime.fromtimestamp(msg.timestamp).strftime(('%d.%m.%Y %H:%M:%S'))
        else:
            if cfg.ini['hirestime']:
                timeStamp = str(msg.timestamp)
            else:
                timeStamp = str(int(msg.timestamp))
        self.handleData(decoded_DBC, timeStamp)

    def handleData(self, DataSet: dict, timeStamp: int):
        """ handleData()
        handles a DataSet and puts the Data into the DataStore
        generates the csv for this Store and puts data and the given timeStamp into the CSV if necessary

        Args:
            DataSet (dict): [description]
            timeStamp (int): [description]
        """
        while (DS.ds[self.MyName]['Commons']['Flag']):
            pass
        DS.ds[self.MyName]['Commons']['Flag'] = True
        
        try:
            if self.MyName != '__DaBo': # dont count yourself
                self.dabodict['__DaBo']['updated DataSets'] = DS.ds['__DaBo']['updated DataSets']['CURRENT_DATA'] + 1
                handle_DataSet(self.dabodict)
        except: pass
        
        if DS.ds[self.MyName]['Commons']['TIMEOUT'] == 0 and DS.ds[self.MyName]['Commons']['RELOAD_TIMEOUT'] != 0:
            logger.info(f'Message send resume: {self.MyName}')
            mi.mailit(f'Message send resume: {self.MyName}')
        DS.ds[self.MyName]['Commons']['Active'] = True
        DS.ds[self.MyName]['Commons']['Counter'] += 1
        DS.ds[self.MyName]['Commons']['TIMEOUT'] = DS.ds[self.MyName]['Commons']['RELOAD_TIMEOUT']
        DS.ds[self.MyName]['Commons']['lastUPD'] = datetime.datetime.now()
        
        for StoreShelf in DataSet:
            if StoreShelf == 'Commons':
                logger.warning(f"Commons can not be updated with handleData()")
                continue
            if StoreShelf not in DS.ds[self.MyName]:
                logger.warning(f"DataSet: {StoreShelf} is not in Store: {self.MyName}")

        csv_line = timeStamp
                       
        Changed = False
        for StoreShelf in DS.ds[self.MyName]:
            if StoreShelf == 'Commons':
                continue
            # complete incomplete DataSets with CURRENT_DATA
            if StoreShelf not in DataSet:
                DataSet[StoreShelf] = DS.ds[self.MyName][StoreShelf]['CURRENT_DATA']

            changed = self.updateData(StoreShelf, DataSet.get(StoreShelf))
            if changed == None:
                continue
            Changed |= changed
            newVal = DS.ds[self.MyName][StoreShelf]['CSV_MODE_DATA']
            try:
                x = DS.ds[self.MyName][StoreShelf]['DECIMALS'] 
                if x != 0:
                    resstr = str(round(float(newVal), x))
                else:
                    resstr = str(int(newVal))
            except: 
                resstr = str(newVal)

            if DS.ds[self.MyName]['Commons']['CSV_FORMAT'] == 'SINGLE' and changed:
                self.writeDataSet(StoreShelf, csv_line + ',' + resstr)
                continue
                
            if (DS.ds[self.MyName]['Commons']['CSV_FORMAT'] == 'MULTI'):
                try:
                    resstr = str(round(DS.ds[self.MyName][StoreShelf]['CSV_MODE_DATA'], x))
                except:
                    resstr = str(DS.ds[self.MyName][StoreShelf]['CSV_MODE_DATA'])
                try:
                    DS.ds[self.MyName]['Commons']['FILLED_UP']
                except Exception as e:
                    if not changed:
                        resstr = ''
                csv_line = csv_line + ',' + resstr
        if (DS.ds[self.MyName]['Commons']['CSV_FORMAT'] == 'MULTI') and Changed:
            self.writeDataSet(StoreShelf, csv_line)
        try:
            if (DS.ds[self.MyName]['Commons']['YML_FORMAT'] == 'CUMULATE'):
                mode = 'a'
            if (DS.ds[self.MyName]['Commons']['YML_FORMAT'] == 'SINGLE'):
                mode = 'w'
            try:
                with open(f"{cfg.ini['DataPath']}/{self.MyName}.yml", mode) as file:
                    yaml.dump(DataSet, file, default_flow_style=False, allow_unicode=True)
            except Exception as err:
                logger.error(f"writing yml-file failed: {err}")
        except:
            pass
        self.DataBase()
        DS.ds[self.MyName]['Commons']['Flag'] = False
        
    def updateData(self, DataShelf: str, DataBoxValue) -> bool:
        """ updateData()
        puts the value into DataBox CSV_MODE_DATA in the DataShelf

        Args:
            DataShelf (str): 
            DataBoxValue (any):

        Returns:
            bool: if an update is done True otherwise False
        """

        try:
            oldDataBoxValue = DS.ds[self.MyName][DataShelf]['CURRENT_DATA']
            DS.ds[self.MyName][DataShelf]['CURRENT_DATA'] = DataBoxValue
        except Exception as err:
            logger.error(f'{type(err).__name__} in: {self.MyName} - {DataShelf}')
            return None
        try:
            if self.MyName != '__DaBo': # dont count yourself
                self.dabodict['__DaBo']['updated Data'] = DS.ds['__DaBo']['updated Data']['CURRENT_DATA'] + 1
                self.dabodict['__DaBo']['last sender'] = self.MyName
                if oldDataBoxValue != DataBoxValue:
                    self.dabodict['__DaBo']['changed Data'] = DS.ds['__DaBo']['changed Data']['CURRENT_DATA'] + 1
                #handle_DataSet(self.dabodict)
        except: pass
                    
        try: # values can be omitted in the *.signals.yml
            DS.ds[self.MyName][DataShelf]['CURRENT_IN_RANGE'] = DS.ds[self.MyName][DataShelf]['CURRENT_DATA'] >= \
                                                                DS.ds[self.MyName][DataShelf]['MIN'] and \
                                                                DS.ds[self.MyName][DataShelf]['CURRENT_DATA'] <= \
                                                                DS.ds[self.MyName][DataShelf]['MAX']
            if (not DS.ds[self.MyName][DataShelf]['CURRENT_IN_RANGE']):
                threading.Thread(target=DS.ds[self.MyName][DataShelf]['CaBa_1'], daemon=True).start() 
                DS.ds[self.MyName]['Commons']['CaBa_1']
                
        except: pass                                                                
        try:
            if(DS.ds[self.MyName][DataShelf]['CSV_MODE'] == 'NONE'):
                return None
        except Exception:
            return None
        if(DS.ds[self.MyName][DataShelf]['CSV_MODE'] == 'ALL'):
            DS.ds[self.MyName][DataShelf]['CSV_MODE_DATA'] = DataBoxValue
            self.processValue(DataShelf, DataBoxValue)
            return True
        if(DS.ds[self.MyName][DataShelf]['CSV_MODE'] == 'CHANGE'):
            if(DS.ds[self.MyName][DataShelf]['CSV_MODE_DATA'] != DataBoxValue):
                DS.ds[self.MyName][DataShelf]['CSV_MODE_DATA'] = DataBoxValue
                self.processValue(DataShelf, DataBoxValue)
                return True
            else: return False
        if(DS.ds[self.MyName][DataShelf]['CSV_MODE'] == 'COUNT'):
            if(DS.ds[self.MyName][DataShelf]['CNT']):
                DS.ds[self.MyName][DataShelf]['CNT'] -= 1
                return False
            else:
                DS.ds[self.MyName][DataShelf]['CNT'] = DS.ds[self.MyName][DataShelf]['RELOAD_CNT'] - 1
                DS.ds[self.MyName][DataShelf]['CSV_MODE_DATA'] = DataBoxValue
                self.processValue(DataShelf, DataBoxValue)
                return True
        if(DS.ds[self.MyName][DataShelf]['CSV_MODE'] == 'AVR'):
            if DS.ds[self.MyName][DataShelf]['CNT']:
                DS.ds[self.MyName][DataShelf]['CNT'] -= 1
                DS.ds[self.MyName][DataShelf]['AVR_SUBTOTAL'] += DataBoxValue
                return False		   
            else:
                DS.ds[self.MyName][DataShelf]['CNT'] = DS.ds[self.MyName][DataShelf]['RELOAD_CNT'] - 1
                DS.ds[self.MyName][DataShelf]['CSV_MODE_DATA'] = (DS.ds[self.MyName][DataShelf]['AVR_SUBTOTAL'] + DataBoxValue) / \
                                                    DS.ds[self.MyName][DataShelf]['RELOAD_CNT']
                DS.ds[self.MyName][DataShelf]['AVR_SUBTOTAL'] = 0
                self.processValue(DataShelf, DS.ds[self.MyName][DataShelf]['CSV_MODE_DATA'])
                return True


    def processValue(self, DataShelf: str, value):
        """ processValue()
        checks wether a value is in a range or not and puts the result into
        DS.ds[self.MyName][DataShelf]['CURRENT_IN_RANGE']
        
        Args:
            DataShelf (str): name of the Shelf in store of this instance
            value (_type_): not needed yet
        """
        DS.ds[self.MyName][DataShelf]["lastUPD"] = datetime.datetime.now()
        try:
            DS.ds[self.MyName][DataShelf]['CURRENT_IN_RANGE'] = DS.ds[self.MyName][DataShelf]['CSV_MODE_DATA'] >= \
                                                                DS.ds[self.MyName][DataShelf]['MIN'] and \
                                                                DS.ds[self.MyName][DataShelf]['CSV_MODE_DATA'] <= \
                                                                DS.ds[self.MyName][DataShelf]['MAX']
        except KeyError:
            pass

    def mergeOperation(self, data, str: str):
        """ mergeOperation() 
        does th operations nor done by merge() itself

        Args:
            data (any): currently not needed
            str (str): MERGE-string from th Datastore.yml

        Returns:
            any: result of the operation
        """
        if str[1] == 'and':
            data[self.MyName][str[-1][0]] = True
            for i in str[2:-1]:
                data[self.MyName][str[-1][0]] = data[self.MyName][str[-1][0]] and DS.ds[i[0]][i[1]][i[2]]
        if str[1] == 'or':
            data[self.MyName][str[-1][0]] = False
            for i in str[2:-1]:
                data[self.MyName][str[-1][0]] = data[self.MyName][str[-1][0]] or DS.ds[i[0]][i[1]][i[2]]
        if str[1] == 'add':
            data[self.MyName][str[-1][0]] = 0
            for i in str[2:-1]:
                data[self.MyName][str[-1][0]] += DS.ds[i[0]][i[1]][i[2]]
        return data

    def _merge_thread(self, sleep, index):
        """ merge() 
        parses the MERGE-string from th Datastore.yml for this Datastore instance and performs the requested action
        """
        mergeStr = DS.ds[self.MyName]['Commons']['MERGE'][index]
        while True:
            data = dict()
            data[self.MyName] = dict()
            try:
                DS.ds[self.MyName]['Commons']['TIMEOUT'] = DS.ds[self.MyName]['Commons']['RELOAD_TIMEOUT']
                DS.ds[self.MyName]['Commons']['Active'] = True
                if mergeStr[1] == 'get':
                    data[self.MyName][mergeStr[3][0]] = DS.ds[mergeStr[2][0]][mergeStr[2][1]][mergeStr[2][2]]
                elif mergeStr[1] == 'cmpc':
                    data[self.MyName][mergeStr[3][0]] = str(DS.ds[mergeStr[2][0]][mergeStr[2][1]][mergeStr[2][2]]) == str(mergeStr[4])
                elif mergeStr[1] == 'andc':
                    data[self.MyName][mergeStr[3][0]] = bool(DS.ds[mergeStr[2][0]][mergeStr[2][1]][mergeStr[2][2]]) & mergeStr[4]
                elif mergeStr[1] == 'orc':
                    data[self.MyName][mergeStr[3][0]] = bool(DS.ds[mergeStr[2][0]][mergeStr[2][1]][mergeStr[2][2]]) | mergeStr[4]
                elif mergeStr[1] == 'lut':
                    data[self.MyName][mergeStr[3]] = ''
                    for lota in mergeStr[5:]:
                        data[self.MyName][mergeStr[1]] += lota[1] + ' | '
                else: data = self.mergeOperation(data, mergeStr)
                self.handle_DataSet(data)
            except Exception as err:
                logging.error(f'merging error: {err}, in store {self.MyName}.')
                pass
            time.sleep(sleep)
                    
    def DataBase(self):
        """
        The function is a method called "DataBase" that attempts to execute the "doRRD" method and
        logs any exceptions that occur.
        """
        # print('DataBase: ', self.MyName)
        try:
            self.doRRD()
        except Exception as err:    
            logger.error(f'fehlr in RRD-Verarbeitung: {type(err).__name__} in: {self.MyName}')

    def doRRD(self):
        """
        The function `doRRD` updates RRD (Round Robin Database) files with values obtained from a data
        source.
        :return: nothing (None).
        """
        try:
            DBInfo = DS.ds[self.MyName]['Commons']['RRD_DB']
        except: 
            #print('no RRD-handling')
            return
        for block in range(len(DBInfo)):
            rrdstr = 'N'
            for line in range(len(DBInfo[block])):
                res = self.getRRDValue(DBInfo[block][line])
                #logger.debug(f"---> {res}")
                if DBInfo[block][line][0] == 'OUTFILE':
                    rrdfile = f"{cfg.ini['RRDPath']}/{str(res)}.rrd"
                else: rrdstr += ':' + str(res)
            #logger.debug(f'calling rrdtool with: {rrdfile} {rrdstr}')
            err = os.system(f'rrdtool update {rrdfile} {rrdstr}')
            if err:
                logger.warning(f'write RRD failed: {rrdfile} - {rrdstr}')
        return    

    def getRRDValue(self, DBStr: str):
        """
        The function `getRRDValue` retrieves a value from a database based on the input `DBStr` and
        returns it.
        
        :param DBStr: The parameter `DBStr` is a string that represents a database query. It is expected
        to have the following structure:
        :type DBStr: str
        :return: the value obtained from the given DBStr.
        """
        if DBStr[0][0] != '§':
            store = self.MyName
        else:
            store = DBStr[0][1:]

        if DBStr[1] == 'CONST':
            value = DBStr[2]
        elif DBStr[1][0] == '§':
            value = DS.ds[store][DBStr[1][1:]][DBStr[2]]
        else: logger.error(f"error in RRD Command string. {DBStr}")
        if DBStr[0] == 'INFILE':
            try:
                with open(f"{cfg.ini['DataPath']}/{value}", 'r') as file:
                    value = file.read()
            except:
                logger.warning(f"File not found: {cfg.ini['DataPath']}{value}")
        # print('getRRDValue (store): ', store, ' - ', value)
        return value

    def writeDataSet(self, Shelf: str, line: str):
        """
        The function `writeDataSet` writes a line of data to a file, either appending it to an existing
        file or creating a new file if it doesn't exist.
        
        :param Shelf: The `Shelf` parameter is a string that is only used when the `CSV_FORMAT` in
        `DS.ds[self.MyName]['Commons']` is set to `'SINGLE'`. It is used to specify the shelf
        associated with the line being written to the CSV file
        :type Shelf: str
        :param line: The `line` parameter is a string that represents a single line of data that you
        want to write into a CSV file
        :type line: str
        """
        if (cfg.ini['humanTimestamp']) or cfg.ini['hirestime']:
            ext = 'csv'
        else:
            ext = 'txt'
        if DS.ds[self.MyName]['Commons']['CSV_FORMAT'] == 'SINGLE':
            FileName = f"{cfg.ini['DataPath']}/{self.MyName}_{Shelf}_{DS.ds[self.MyName][Shelf]['CSV_MODE']}{DS.ds[self.MyName]['Commons']['initTime'].strftime(cfg.ini['dataSuffix'])}.{ext}"
            DS.ds[self.MyName]['Commons']['header'] = f'time,{Shelf}'
        if DS.ds[self.MyName]['Commons']['CSV_FORMAT'] == 'MULTI':
            FileName = f"{cfg.ini['DataPath']}/{self.MyName}{DS.ds[self.MyName]['Commons']['initTime'].strftime(cfg.ini['dataSuffix'])}.{ext}"
        try:
            with open(FileName, 'r') as DataFile: 
                pass
        except:        
            line = DS.ds[self.MyName]['Commons']['header'] + '\n' + line
        with open(FileName, 'a') as DataFile: 
            DataFile.write(line + '\n')
            DataFile.close()

def pick(Store, Shelf, DataBox):
    """
    The function "pick" retrieves data from a nested dictionary structure based on the provided store,
    shelf, and data box parameters.
    
    :param Store: The parameter "Store" represents the store where the data is stored. It could be a
    specific location or identifier for the store
    :param Shelf: The "Shelf" parameter refers to the specific shelf within a store where the data is
    located
    :param DataBox: The `DataBox` parameter represents the specific data box within a shelf in a store
    :return: the value stored in the specified DataBox, located on the specified Shelf, within the
    specified Store. If the specified Store, Shelf, or DataBox does not exist, the function will return
    None.
    """
    try:
        return DS.ds[Store][Shelf][DataBox]
    except:
        return None

def put(Store, *args):
    """
    The `put` function takes a store and a variable number of arguments, creates a dictionary `data`,
    retrieves data from each shelf in the store (except for 'Commons'), and then adds the additional
    arguments to the `data` dictionary before passing it to the `handle_DataSet` function.
    
    :param Store: The "Store" parameter represents the name of the store or location where the data will
    be stored
    """
    data = {Store: {}}
    for Shelf in DS.ds[Store]:
        if Shelf != 'Commons':
            data[Store][Shelf] = pick(Store, Shelf, 'CURRENT_DATA')
    for arg in args:
        data[Store][arg[0]] = arg[1]
    handle_DataSet(data)

def handle_DataSet(DataSet: dict):
    """
    The function `handle_DataSet` takes a dictionary `DataSet` as input and attempts to call a method
    `handle_DataSet` on a service object stored in a data store. If the data store is unknown, it logs
    an error message.
    
    :param DataSet: The `DataSet` parameter is a dictionary that contains data to be processed. It is
    assumed that the dictionary has at least one key-value pair
    :type DataSet: dict
    """
    DS.ds[list(DataSet.keys())[0]]['Commons']['Service'].handle_DataSet(DataSet)
    try:
        DS.ds[list(DataSet.keys())[0]]['Commons']['Service'].handle_DataSet(DataSet)
    except Exception:
        logger.info(f'unknown Datastore: {DataSet.keys()}')

def handle_CAN(StoreName, DataSet):
    """
    The function handle_CAN takes in a StoreName and DataSet as parameters and calls the handle_CAN
    method of the Service object in the Commons dictionary of the ds object in the DS module.
    
    :param StoreName: The StoreName parameter is a string that represents the name of the store or
    database where the data is stored
    :param DataSet: The DataSet parameter is a collection of data that needs to be processed or
    analyzed. It could be in the form of a list, dictionary, or any other data structure that can hold
    CSV_FORMATple values
    """
    DS.ds[StoreName]['Commons']['Service'].handle_CAN(DataSet)
    
def setCallBack(store, shelf, function):
    try:
        DS.ds[store]['Commons']['Service'].setCallBack(shelf, function)
    except Exception as err:
        logger.info(f'unknown Datastore in setCallBack({store}, {function}) -> {err}')