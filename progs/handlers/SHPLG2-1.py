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
    data['name'] = self.this['device']['Hostname']
    data['Type'] = self.this['device']['Type']
    data['IP'] = self.this['device']['IP']
    data['Power'] = self.this['response'].text
    power = json.loads(data["Power"])
    power_value = power["power"]
    data['Power'] = power_value
    data['Hardware'] = self.this['device']['Hardware']
    return data
