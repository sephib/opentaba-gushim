import logging
import logging.config
import os
import shutil
import requests
import datetime

from gushim import utilities


def get_gushim(folder, url=None):
    logger = utilities.get_logger()
    if not url:
        logger.error('Need URL to download file from ')
        return FileNotFoundError
    data = get_data_from_url(url)
    name = 'file_download'
    file_name = save_file(folder, name, data)
    logger.debug('Successfuly downloaded file: {0}'.format(file_name))
    return file_name


def get_data_from_url(url):
    response = requests.get(url, stream=True)
    return response.raw


def save_file(folder, name, data):
    logger = utilities.get_logger()
    file_name = os.path.join(folder, name + '.zip')
    with open(file_name, 'wb') as fout:
        shutil.copyfileobj(data, fout)

    datetime_stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    file_name_with_date = 'MapiGushim{0}{1}'.format(datetime_stamp, '.zip')
    new_file_name = os.path.join(folder,file_name_with_date)
    os.rename(file_name, new_file_name)
    logger.info('Downloaded and saved file {0}'.format(new_file_name))
    return new_file_name


def get_mapi_uncompress_file(folder_path, mapi_format):
    """
    :param folder_path: Location of the unzip file
    :param mapi_format: The file format of the gushim unzipped file - currently csv
    :return: return filename
    """
    for (dir_path, dir_names, file_names) in os.walk(folder_path):
        csv_files = [os.path.join(dir_path, fi) for fi in file_names if fi.endswith(mapi_format)][0]
    return csv_files
