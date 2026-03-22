from dispatcher import Dispatcher
import logging
import json

logger = logging.getLogger(__name__)
logging.getLogger('urllib3').setLevel(logging.WARNING)

@Dispatcher.register("S4PL-00416EU")
def handle_S4PL(self):
    logger.debug("Handling: S4PL-00416EU")
    data = json.loads(self.this['response'].text)
    return data
