from dispatcher import Dispatcher
import logging
import ESP_parser
import requests

logger = logging.getLogger(__name__)
logging.getLogger('urllib3').setLevel(logging.WARNING)

@Dispatcher.register("ToF")
def handle_tof(self):
    logger.debug("Handling: ToF")
    text = self.this['response'].text
    data = ESP_parser.parse_ESP_main(text)
    data['name'] = self.this['device']['Hostname'][:-18] + '-' + self.this['device']['Hostname'][-17:]
    data['Type'] = self.this['device']['Type']
    data['IP'] = self.this['device']['IP']  
    data.pop('Network-IP', None)  # entfernen, da nicht relevant
    res = requests.get(f"http://{self.this['device']['IP']}/status") #{self.this['InfoURL']}")
    y = ESP_parser.parse_ESP_tof(res.text)
    data['distance'] = y
    return data
