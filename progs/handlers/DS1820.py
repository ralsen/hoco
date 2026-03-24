from dispatcher import Dispatcher
import logging
import ESP_parser
import requests

logger = logging.getLogger(__name__)
logging.getLogger('urllib3').setLevel(logging.WARNING)

@Dispatcher.register("DS1820")
def handle_DS1820(self):
    logger.debug("Handling DS1820")
    text = self.this['response'].text
    data = ESP_parser.parse_ESP_main(text)
    data['name'] = self.this['device']['Hostname'][:-18] + '-' + self.this['device']['Hostname'][-17:]
    data['Type'] = self.this['device']['Type']
    data['IP'] = self.this['device']['IP']  
    data.pop('Network-IP', None)  # entfernen, da nicht relevant
    res = requests.get(f"http://{self.this['device']['IP']}/status") #{self.this['InfoURL']}")
    y = ESP_parser.parse_ESP_table(res.text)
    data['Type'] = data['Type'] + '-' + str (len(y))
    for count, i in enumerate(y):
        print(count)
        channel = i.get('channel')
        temp = i.get('Temperatur')
        if channel and temp:
            data[f'Adress_{count}'] = channel
            data[f'Value_{count}'] = temp
    
    return data
