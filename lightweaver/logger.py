import logging

from mpi4py import MPI

from os.path import abspath

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

class MPIFileHandler(logging.FileHandler):                                      
    def __init__(self,
                 filename,
                 mode=MPI.MODE_WRONLY|MPI.MODE_CREATE|MPI.MODE_APPEND ,
                 encoding='utf-8',  
                 delay=False,
                 comm=MPI.COMM_WORLD ):                                                
        self.baseFilename = abspath(filename)                           
        self.mode = mode                                                        
        self.encoding = encoding                                            
        self.comm = comm                                                        
        if delay:                                                               
            #We don't open the stream, but we still need to call the            
            #Handler constructor to set level, formatter, lock etc.             
            logging.Handler.__init__(self)                                      
            self.stream = None                                                  
        else:                                                                   
           logging.StreamHandler.__init__(self, self._open())                   
                                                                                
    def _open(self):                                                            
        stream = MPI.File.Open( self.comm, self.baseFilename, self.mode )     
        stream.Set_atomicity(True)                                              
        return stream
                                                    
    def emit(self, record):
        """
        Emit a record.
        If a formatter is specified, it is used to format the record.
        The record is then written to the stream with a trailing newline.  If
        exception information is present, it is formatted using
        traceback.print_exception and appended to the stream.  If the stream
        has an 'encoding' attribute, it is used to determine how to do the
        output to the stream.
        
        Modification:
            stream is MPI.File, so it must use `Write_shared` method rather
            than `write` method. And `Write_shared` method only accept 
            bytestring, so `encode` is used. `Write_shared` should be invoked
            only once in each all of this emit function to keep atomicity.
        """
        try:
            msg = self.format(record)
            stream = self.stream
            stream.Write_shared((msg+self.terminator).encode(self.encoding))
            #self.flush()
        except Exception:
            self.handleError(record)        

def buildLogger(NameAtCall, loggerMPI = False):
    if loggerMPI:
        comm=MPI.COMM_WORLD
        logger = logging.getLogger("rank[%i]"%comm.rank + NameAtCall)
    else:
        logger = logging.getLogger(NameAtCall)
    
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        if loggerMPI:
            ch = MPIFileHandler("rank[%i]"%comm.rank + "_MPI_logfile.log")
        else:
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