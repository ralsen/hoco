import importlib
import pkgutil
import logging
logger = logging.getLogger(__name__)
logging.getLogger('urllib3').setLevel(logging.WARNING)

class Dispatcher:

    handlers = {}

    @classmethod
    def register(cls, device_type):
        logger.debug(f"Registering handler for device type: {device_type}")
        def decorator(func):
            logger.debug(f"Registering function '{func.__name__}' for device type '{device_type}'")
            cls.handlers[device_type] = func
            return func
        return decorator

    def __init__(self, this):
        self.this = this

    def handle(self):
        device_type = self.this.get('Type')
        handler = self.handlers.get(device_type)

        if handler:
            return handler(self)   # freie Funktion → self übergeben
        else:
            return self.handle_default()  # gebundene Methode → OHNE self
        
    def handle_default(self):
        logger.debug(f"Unbekannter Typ: {self.this.get('Type')}")
        return None


def load_handlers():
    import handlers  # Paket

    for _, module_name, _ in pkgutil.iter_modules(handlers.__path__):
        logger.debug(f"Loading handler module: {module_name}")
        importlib.import_module(f"{handlers.__name__}.{module_name}")
