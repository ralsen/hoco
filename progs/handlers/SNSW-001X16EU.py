from dispatcher import Dispatcher
import logging
import json

logger = logging.getLogger(__name__)
logging.getLogger('urllib3').setLevel(logging.WARNING)

@Dispatcher.register("SNSW-001X16EU")
def handle_SNSW(self):
    logger.debug("Handling: SNSW-001X16EU")
    data = json.loads(self.this['response'].text)
    return data
