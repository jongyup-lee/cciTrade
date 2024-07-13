import logging
from datetime import datetime

class Logging():
    def __init__(self) -> None:
        pass

    def setLogging(self, kind, context):

        today = datetime.today().date()

        logging.basicConfig(filename=f'../logs/systemTrading_{today}.log', level=logging.DEBUG,
                            format="[ %(asctime)s | %(levelname)s ] %(message)s",
                            datefmt="%Y-%m-%d %H:%M:%S")
        self.logger = logging.getLogger()

        if kind == 'info':
            self.logger.info(context)
        elif kind == 'debug':
            self.logger.debug(context)
