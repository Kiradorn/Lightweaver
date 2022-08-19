import logging

from mpi4py import MPI

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from pathlib import Path

    from mpi4py import MPI

    _MPI_APPEND_MODE = MPI.MODE_CREATE | MPI.MODE_APPEND

logging.getLogger(__name__)


'''
Might be nice to add some rank information to the printed statements at some point for the MPI case
'''

class CustomFormatter(logging.Formatter):

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

class MPIFileStream:
    """Wrap MPI.File` so it has the same API as python file streams.

    Parameters
    ----------
    filename : Path
        disk location of the file stream
    MPI : MPI
        MPI communicator object
    mode : str, optional
        file write mode, by default _MPI_APPEND_MODE
    """

    def __init__(
        self, filename: "Path", MPI: "MPI", mode: str = "_MPI_APPEND_MODE"
    ) -> None:
        self.stream = MPI.File.Open(MPI.COMM_WORLD, filename, mode)
        self.stream.Set_atomicity(True)
        self.name = "MPIfilestream"

    def write(self, msg: str):
        """Write to MPI shared file stream.

        Parameters
        ----------
        msg : str
            message to write
        """
        b = bytearray()
        b.extend(map(ord, msg))
        self.stream.Write_shared(b)

    def close(self):
        """Synchronize and close MPI file stream."""
        self.stream.Sync()
        self.stream.Close()


class MPIHandler(logging.FileHandler):
    """Emulate `logging.FileHandler` with MPI shared File that all ranks can write to.

    Parameters
    ----------
    filename : Path
        file path
    MPI : MPI
        MPI communicator object
    mode : str, optional
        file access mode, by default "_MPI_APPEND_MODE"
    """

    def __init__(
        self,
        filename: "Path",
        MPI: "MPI",
        mode: str = "_MPI_APPEND_MODE",
    ) -> None:
        self.MPI = MPI
        super().__init__(filename, mode=mode, encoding=None, delay=False)

    def _open(self):
        return MPIFileStream(self.baseFilename, self.MPI, self.mode)

    def setStream(self, stream):
        """Stream canot be reasigned in MPI mode."""
        raise NotImplementedError("Unable to do for MPI file handler!")   



# def buildLogger(NameAtCall, loggerMPI = False):
def buildLogger(
    level: int,
    log_path: Optional["Path"] = None,
    mpi_log: Optional[bool] = False
):

    
    logger = logging.getLogger()
    logger.setLevel(level)

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    MPI = None
    if mpi_log:
        try:
            from mpi4py import MPI
        except ImportError as e:
            raise RuntimeError("You cannot specify 'loggerMPI' when mpi4py not installed") from e

    ch = logging.StreamHandler()
    ch.setFormatter(CustomFormatter())
    ch.setLevel(level)

    logger.addHandler(ch)

    if log_path:
        
        fh = None

        if mpi_log:
            fh = MPIHandler(log_path, MPI, mode=MPI.MODE_WRONLY | MPI.MODE_CREATE | MPI.MODE_APPEND)
            fh.setFormatter(CustomFormatter())
        else:
            fh = logging.FileHandler(log_path, mode=MPI.MODE_WRONLY | MPI.MODE_CREATE | MPI.MODE_APPEND)
            fh.setFormatter(CustomFormatter())

        if fh:
            fh.setLevel(level)
            logger.addHandler(fh)


def closeLogger(logger):
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()