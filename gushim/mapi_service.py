import logging
import logging.config
import os
import shutil
import requests
import datetime


def get_gushim(folder, url=None):
    logger = logging.getLogger(__name__)
    if not url:
        logger.warning('Need URL to download file from ')
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
    logger = logging.getLogger(__name__)
    file_name = os.path.join(folder, name + '.zip')
    with open(file_name, 'wb') as fout:
        shutil.copyfileobj(data, fout)

    datetime_stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    file_name_with_date = 'MapiGushim{0}{1}'.format(datetime_stamp, '.zip')
    os.rename(file_name, file_name_with_date)
    logger.info('Downloaded and saved file {0}'.format(file_name_with_date ))
    return file_name_with_date
