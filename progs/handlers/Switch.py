from dispatcher import Dispatcher
import logging
import ESP_parser

logger = logging.getLogger(__name__)
logging.getLogger('urllib3').setLevel(logging.WARNING)

@Dispatcher.register("Switch")
def handle_switch(self):
    logger.debug("Handling: Switch")
    text = self.this['response'].text
    return ESP_parser.parse_ESP(text)
