from dispatcher import Dispatcher
import logging
import ESP_parser

logger = logging.getLogger(__name__)
logging.getLogger('urllib3').setLevel(logging.WARNING)

@Dispatcher.register("ToF")
def handle_tof(self):
    logger.debug("Handling: ToF")
    text = self.this['response'].text
    return ESP_parser.parse_ESP(text)
