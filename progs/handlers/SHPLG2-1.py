from dispatcher import Dispatcher
import logging
import json

logger = logging.getLogger(__name__)
logging.getLogger('urllib3').setLevel(logging.WARNING)

@Dispatcher.register("SHPLG2-1")
def handle_sHPLG2(self):
    logger.debug("Handling: SHPLG2-1")
    data = json.loads(self.this['response'].text)
    return data
