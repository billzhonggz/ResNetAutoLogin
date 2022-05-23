import sys
from typing import Union
from pathlib import Path
from datetime import timedelta

import logging

DEFAULT_WORK_DIR = 'logs'

def str_to_path(p: Union[str, Path]) -> Path:
    if isinstance(p, str):
        return Path(p)
    else:
        return p


def setup_logger(work_dir=None, logfile_name=None, logger_name='logger') -> logging.Logger:
    """Sets up logger from target work directory.

    The function will sets up a logger with `DEBUG` log level. Two handlers will
    be added to the logger automatically. One is the `sys.stdout` stream, with
    `INFO` log level, which will print improtant messages on the screen. The other
    is used to save all messages to file `$WORK_DIR/$LOGFILE_NAME`. Messages will
    be added time stamp and log level before logged.

    NOTE: If `logfile_name` is empty, the file stream will be skipped. Also,
    `DEFAULT_WORK_DIR` will be used as default work directory.

    Args:
      work_dir: The work directory. All intermediate files will be saved here.
        (default: None)
      logfile_name: Name of the file to save log message. (default: `log.txt`)
      logger_name: Unique name for the logger. (default: `logger`)

    Returns:
      A `logging.Logger` object.

    Raises:
      SystemExit: If the work directory has already existed, of the logger with
        specified name `logger_name` has already existed.

    This function is borrowed from HiGAN (https://github.com/genforce/higan).
    """

    logger = logging.getLogger(logger_name)
    if logger.hasHandlers():  # Already existed
        raise SystemExit(f'Logger name `{logger_name}` has already been set up!\n'
                         f'Please use another name, or otherwise the messages '
                         f'may be mixed between these two loggers.')

    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("[%(asctime)s][%(levelname)s] %(message)s")

    # Print log message with `INFO` level or above onto the screen.
    sh = logging.StreamHandler(stream=sys.stdout)
    sh.setLevel(logging.INFO)
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    if not logfile_name:
        return logger

    work_dir = work_dir or DEFAULT_WORK_DIR
    work_dir = str_to_path(work_dir)
    logfile_name = work_dir.joinpath(logfile_name)
    work_dir.mkdir(exist_ok=True, parents=True)

    # Save log message with all levels in log file.
    fh = logging.FileHandler(logfile_name)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger


UNITS = {"s":"seconds", "m":"minutes", "h":"hours", "d":"days", "w":"weeks"}

def convert_to_seconds(s: str) -> int:
    count = int(s[:-1])
    unit = UNITS[ s[-1] ]
    td = timedelta(**{unit: count})
    return td.seconds + 60 * 60 * 24 * td.days