import logging

class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    grey = "\x1b[38;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    FORMATS = {
        logging.DEBUG: "[" + grey + "%(levelname)-8s" + reset +"]: " + "%(asctime)s:  %(name)s - %(message)s (%(filename)s:%(lineno)d)",
        logging.INFO: "[" + grey + "%(levelname)-8s" + reset +"]: " + "%(asctime)s: " + "%(message)s",
        logging.WARNING: "[" + yellow + "%(levelname)-8s" + reset +"]: " + "%(asctime)s: " + "%(message)s",
        logging.ERROR: "[" + red + "%(levelname)-8s" + reset +"]: " + "%(asctime)s: " + "%(message)s" + " (%(filename)s:%(lineno)d)",
        logging.CRITICAL: "[" + bold_red + "%(levelname)-8s" + reset +"]: " + "%(asctime)s: " + "%(message)s" + " (%(filename)s:%(lineno)d)"
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

def buildLogger(NameAtCall):
    logger = logging.getLogger(NameAtCall)
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(CustomFormatter())
    logger.addHandler(ch)
    return logger