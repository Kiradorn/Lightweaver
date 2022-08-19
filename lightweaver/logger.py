import logging

class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    # grey = "\x1b[38;21m"
    # yellow = "\x1b[33;21m"
    # red = "\x1b[31;21m"
    # bold_red = "\x1b[31;1m"
    # reset = "\x1b[0m"

    # FORMATS = {
    #     logging.DEBUG: "lw : [" + grey + "%(levelname)-8s" + reset +"]: " + "%(asctime)s:  %(name)s - %(message)s (%(filename)s:%(lineno)d)",
    #     logging.INFO: "lw : [" + grey + "%(levelname)-8s" + reset +"]: " + "%(asctime)s: " + "%(message)s",
    #     logging.WARNING: "lw : [" + yellow + "%(levelname)-8s" + reset +"]: " + "%(asctime)s: " + "%(message)s",
    #     logging.ERROR: "lw : [" + red + "%(levelname)-8s" + reset +"]: " + "%(asctime)s: " + "%(message)s" + " (%(filename)s:%(lineno)d)",
    #     logging.CRITICAL: "lw : [" + bold_red + "%(levelname)-8s" + reset +"]: " + "%(asctime)s: " + "%(message)s" + " (%(filename)s:%(lineno)d)"
    # }

    FORMATS = {
        logging.DEBUG: "lw : ["+"%(levelname)-8s"+"]: " + "%(asctime)s:  %(name)s - %(message)s (%(filename)s:%(lineno)d)",
        logging.INFO: "lw : ["+"%(levelname)-8s"+"]: " + "%(asctime)s: " + "%(message)s",
        logging.WARNING: "lw : ["+"%(levelname)-8s"+"]: " + "%(asctime)s: " + "%(message)s",
        logging.ERROR: "lw : ["+"%(levelname)-8s"+"]: " + "%(asctime)s: " + "%(message)s" + " (%(filename)s:%(lineno)d)",
        logging.CRITICAL: "lw : ["+"%(levelname)-8s"+"]: " + "%(asctime)s: " + "%(message)s" + " (%(filename)s:%(lineno)d)"
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

def buildLogger(NameAtCall):
    logger = logging.getLogger(NameAtCall)
    if not logger.handlers:
	    logger.setLevel(logging.DEBUG)
	    ch = logging.StreamHandler()
	    ch.setLevel(logging.DEBUG)
	    ch.setFormatter(CustomFormatter())
	    logger.addHandler(ch)
    return logger

def closeLogger(logger):
	handlers = logger.handlers[:]
	for handler in handlers:
	    logger.removeHandler(handler)
	    handler.close()