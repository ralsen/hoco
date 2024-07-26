import time
import logging 
import threading

logger = logging.getLogger(__name__)

class driver:
    def __init__(self, driver, iBlock, mBlock):
        self.iBlock = iBlock
        self.mBlock = mBlock
        self.drv = driver
        threading.Thread(target=self._check, daemon=True).start()    
        pass
    
    def _check(self):
        i = 0
        while True:
            on = self.drv.isDeviceOnline(self.mBlock['ip'])
            logger.debug(f"{self.iBlock['hostname']}: {i} is {on}")
            i+=1
            time.sleep(1)