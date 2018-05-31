import re
import time
import logging as lg
import datetime as dt
from . import gushimconfig
import os
import sys
import unicodedata
import yaml
import zipfile



def config(workspace_folder=gushimconfig.WORKSPACE_FOLDER,
           log_folder=gushimconfig.log_folder,
           log_file=gushimconfig.log_file,
           log_console=gushimconfig.log_console,
           log_level=gushimconfig.log_level,
           log_name=gushimconfig.log_name,
           log_filename=gushimconfig.log_filename):
    """
    gushimconfigure by setting the default global vars in gushimgushimconfig.py to desired values.

    Parameters
    ---------
    workspace_folder : string
        where to save and load data files
    logs_folder : string
        where to write the log files
    imgs_folder : string
        where to save figures
    log_file : bool
        if true, save log output to a log file in logs_folder
    log_console : bool
        if true, print log output to the console
    log_level : int
        one of the logger.level constants
    log_name : string
        name of the logger

    Returns
    -------
    None
    """

    # set each global variable to the passed-in parameter value
    gushimconfig.WORKSPACE_FOLDER = workspace_folder
    gushimconfig.logs_folder = log_folder
    gushimconfig.log_console = log_console
    gushimconfig.log_file = log_file
    gushimconfig.log_level = log_level
    gushimconfig.log_name = log_name
    gushimconfig.log_filename = log_filename

    # if logging is turned on, log that we are gushimconfigured
    if gushimconfig.log_file or gushimconfig.log_console:
        log('configured gushim')


class TimeWith(object):
    def __init__(self, name=''):
        self.name = name
        self.start = time.time()

    @property
    def elapsed(self):
        return time.time() - self.start

    def checkpoint(self, name=''):
        print('{timer} {checkpoint} took {elapsed} seconds'.format(
                timer=self.name,
                checkpoint=name,
                elapsed=self.elapsed,
                ).strip())

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.checkpoint('finished')
        pass


def setup_logging(default_path='logging.yaml', default_level=lg.INFO, env_key='LOG_CFG'):
    """
    Setup logging gushimconfiguration
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            gushimconfig = yaml.safe_load(f.read())
        lg.config.dictconfig(gushimconfig)
    else:
        lg.basicConfig(level=default_level)
    logger = lg.getLogger(__name__)
    return logger


def log(message, level=None, name=None, filename=None):
    """
    Write a message to the log file and/or print to the the console.

    Parameters
    ----------
    message : string
        the content of the message to log
    level : int
        one of the logger.level constants
    name : string
        name of the logger
    filename : string
        name of the log file

    Returns
    -------
    None
    """

    if level is None:
        level = gushimconfig.log_level
    if name is None:
        name = gushimconfig.log_name
    if filename is None:
        filename = gushimconfig.log_filename

    # if logging to file is turned on
    if gushimconfig.log_file:
        # get the current logger (or create a new one, if none), then log message at requested level
        logger = get_logger(level=level, name=name, filename=filename)
        if level == lg.DEBUG:
            logger.debug(message)
        elif level == lg.INFO:
            logger.info(message)
        elif level == lg.WARNING:
            logger.warning(message)
        elif level == lg.ERROR:
            logger.error(message)

    # if logging to console is turned on, convert message to ascii and print to the console
    if gushimconfig.log_console:
        # capture current stdout, then switch it to the console, print the message, then switch back to what had been the stdout
        # this prevents logging to notebook - instead, it goes to console
        standard_out = sys.stdout
        sys.stdout = sys.__stdout__

        # convert message to ascii for console display so it doesn't break windows terminals
        message = unicodedata.normalize('NFKD', make_str(message)).encode('ascii', errors='replace').decode()
        print(message)
        sys.stdout = standard_out


def get_logger(level=None, name=None, filename=None):
    """
    Create a logger or return the current one if already instantiated.

    Parameters
    ----------
    level : int
        one of the logger.level constants
    name : string
        name of the logger
    filename : string
        name of the log file

    Returns
    -------
    logger.logger
    """

    if level is None:
        level = gushimconfig.log_level
    if name is None:
        name = gushimconfig.log_name
    if filename is None:
        filename = gushimconfig.log_filename

    logger = lg.getLogger(name)

    # if a logger with this name is not already set up
    if not getattr(logger, 'handler_set', None):

        # get today's date and construct a log filename
        todays_date = dt.datetime.today().strftime('%Y_%m_%d')
        log_filename = '{}/{}_{}.log'.format(gushimconfig.log_folder, filename, todays_date)

        # if the logs folder does not already exist, create it
        if not os.path.exists(gushimconfig.log_folder):
            os.makedirs(gushimconfig.log_folder)

        # create file handler and log formatter and set them up
        handler = lg.FileHandler(log_filename, encoding='utf-8')
        formatter = lg.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)
        logger.handler_set = True

    return logger


def get_or_create_folder(folder_name, current_folder=False):
    """
    :param folder_name: string
    :return: full_path:string
        the path to the folder
    """
    if current_folder:
        relative = os.path.dirname(__file__)
    else:
        relative ='../'
    base_folder = os.path.abspath(relative)
    if not folder_name:
        folder_name = 'workspace'
    full_path = os.path.join(base_folder, folder_name)

    if not os.path.exists(full_path) or not os.path.isdir(full_path):
        print('Creating new directory at {}'.format(full_path))
        os.mkdir(full_path)

    return full_path


def make_str(value):
    """
    Convert a passed-in value to unicode if Python 2, or string if Python 3.

    Parameters
    ----------
    value : any
        the value to convert to unicode/string

    Returns
    -------
    unicode or string
    """
    try:
        # for python 2.x compatibility, use unicode
        return unicode(value)
    except:
        # python 3.x has no unicode type, so if error, use str type
        return str(value)


def zip_uncompress(filename, folder_path=None):
    logger = lg.getLogger(__name__)
    if not folder_path:
        folder_path = os.path.dirname(filename)
    with zipfile.ZipFile(filename, "r") as zip_ref:
        zip_ref.extractall(folder_path)
    logger.debug('Uncompressed file into {0}'.format(folder_path))


def slugify(value, allow_unicode=False):
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces to hyphens.
    Remove characters that aren't alphanumerics, underscores, or hyphens.
    Convert to lowercase. Also strip leading and trailing whitespace.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    value = re.sub(r'[-\s]+', '-', value)
    return value



