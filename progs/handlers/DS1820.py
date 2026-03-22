from dispatcher import Dispatcher
import logging
import ESP_parser

logger = logging.getLogger(__name__)
logging.getLogger('urllib3').setLevel(logging.WARNING)

@Dispatcher.register("DS1820")
def handle_DS1820(self):
    logger.debug("Handling DS1820")
    text = self.this['response'].text
    return ESP_parser.parse_ESP(text)
