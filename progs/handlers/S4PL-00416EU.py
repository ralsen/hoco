from dispatcher import Dispatcher
import logging
import json

logger = logging.getLogger(__name__)
logging.getLogger('urllib3').setLevel(logging.WARNING)

@Dispatcher.register("S4PL-00416EU")
def handle_S4PL(self):
    logger.debug("Handling: S4PL-00416EU")
    data = {}
    data['name'] = self.this['device']['Hostname']
    data['Type'] = self.this['device']['Type']
    data['IP'] = self.this['device']['IP']
    power = json.loads(self.this['response'].text)
    apowers = [v["apower"] for v in power.values() if isinstance(v, dict) and "apower" in v]
    for i in range(len(apowers)):
        data['power_'+ str(i)] = apowers[i]
    return data
