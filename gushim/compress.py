import logging
import logging.config
import gzip
import os
import shutil
import zipfile

class Config(object):
    # General settings
    DEBUG_MODE = 0
    LOGGING_CONFIG_PATH = '/opt/common/logging.json'

    # Modes
    COMPRESS = True

    # Resources
    FOLDER_PATH = os.path.basename(__file__)
    DESTINATION_PATH = ''

    def __init__(self):
        pass

# Create a config instance
config = Config()


def gzip_compress(original_file_name, folder_path):
    with open(os.path.join(folder_path, original_file_name), 'rb') as f_in, gzip.open(
                    os.path.join(folder_path, original_file_name) + ".gz", 'wb') as f_out:
        try:
            shutil.copyfileobj(f_in, f_out)
        except:
            raise


def gzip_uncompress(gz_file, folder_path, destination_path=None):
    logger = logging.getLogger(__name__)
    if destination_path is None:
        destination_path = folder_path

    with gzip.open(os.path.join(folder_path, gz_file), 'rb') as f_in, open(
            os.path.join(destination_path, gz_file[:-3]), 'wb') as f_out:
        try:
            shutil.copyfileobj(f_in, f_out)
        except:
            raise
    logger.info('uncompressed {0}'.format(gz_file))


def zip_uncompress(filename, folder_path=None):
    logger = logging.getLogger(__name__)
    if not folder_path:
        folder_path = os.path.dirname(filename)
    with zipfile.ZipFile(filename, "r") as zip_ref:
        zip_ref.extractall(folder_path)
    logger.info('Uncompressed file into {0}'.format(folder_path))


def main(folder_path):
    if not os.listdir(folder_path).__len__() > 0:
        return FileNotFoundError


if __name__ == '__main__':
    pass

