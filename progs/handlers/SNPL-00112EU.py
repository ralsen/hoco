from dispatcher import Dispatcher
import logging
import json

logger = logging.getLogger(__name__)
logging.getLogger('urllib3').setLevel(logging.WARNING)

@Dispatcher.register("SNPL-00112EU")
def handle_SNPL(self):
    logger.debug("Handling: SNPL-00112EU")
    data = json.loads(self.this['response'].text)
    return data
