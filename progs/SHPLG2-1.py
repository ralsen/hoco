import time
import logging 
import threading

logger = logging.getLogger(__name__)

class driver:
    def __init__(self, iBlock):
        self.iBlock = iBlock
        threading.Thread(target=self._check, daemon=True).start()    
        pass
    
    def _check(self):
        i= 0
        while True:
            logger.debug(f"{self.iBlock['hostname']}: {i}")
            i+=1
            time.sleep(1)