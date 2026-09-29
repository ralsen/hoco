from dispatcher import Dispatcher
import logging
import json

logger = logging.getLogger(__name__)
logging.getLogger('urllib3').setLevel(logging.WARNING)

@Dispatcher.register("SHPLG2-1")
def handle_SHPLG2(self):
    logger.debug("Handling: SHPLG2-1")
    data = {}
    #data = json.loads(self.this['response'].text)
    try:
        data['name'] = self.this['device']['Hostname']
        data['Type'] = self.this['device']['Type']
        data['IP'] = self.this['device']['IP']
        text = json.loads(self.this['response'].text)
        data['Power'] = text['power']
        data['total'] = text['total']
        data['uptime'] = text['timestamp']
        data['Hardware'] = self.this['device']['Hardware']
    except Exception as e:
        logger.error(f"Error occurred while handling SHPLG2-1: {e}")
        data = {}
    return data
