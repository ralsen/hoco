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

    """
    {'Version': 'V5.0f', 'Hostname': 'Buero-68C63A87FACE', 'Type': 'DS1820', 'Hardw': 'NODEMCU', 'Chip-ID': '0x87face', 'MAC-Address': '68:C6:3A:87:FA:CE', 'Network': 'janzneu', 'Network-IP': '192.168.2.38', 'Devicename': 'Buero', 'AP-Name': 'ESPnet', 'cfg-Size': '0x14c', 'Hash': '0x8ffc96', 'Display': 'False', 'uptime': '66 days - 3 hours - 25 minutes - 54 seconds', 'Measuring cycle': '150 s (remainig: 143 s)', 'Transmit cycle': '300 s (remaining: 30 s)', 'PageReload cycle': '10 s', 'Server': '192.168.2.5', 'Port': '8080', 'LED': 'on', 'Signal strength': '-79', 'good Transmissions': '19042', 'bad Transmissions': '7', 'Pages delivered': '671', 'Measurements': '37847'}
    {'name': 'shellyplug-083A8DF437C7', 'Type': 'SHPLG2-1', 'IP': '192.168.2.43', 'Power': 34.2, 'Hardware': 'Shelly'}
    """
    