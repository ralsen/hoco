from dispatcher import Dispatcher
import logging
import json

logger = logging.getLogger(__name__)
logging.getLogger('urllib3').setLevel(logging.WARNING)

@Dispatcher.register("S3PM-001PCEU16")
def handle_3PM(self):
    logger.debug("Handling: S3PM-001PCEU16")
    data = json.loads(self.this['response'].text)
    return data
