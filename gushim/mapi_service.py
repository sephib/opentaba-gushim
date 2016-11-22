import logging
import logging.config
import os
import shutil
import requests




def get_gushim(folder, url):
    # url = 'http://consuming-python-services-api.azurewebsites.net/cats/random'
    data = get_data_from_url(url)
    name = 'file_download'
    file_name = save_file(folder, name, data)
    return file_name


def get_data_from_url(url):
    response = requests.get(url, stream=True)
    return response.raw


def save_file(folder, name, data):
    logger = logging.getLogger(__name__)
    file_name = os.path.join(folder, name + '.zip')
    with open(file_name, 'wb') as fout:
        shutil.copyfileobj(data, fout)

    logger.info('Downloaded and saved file {0}'.format(file_name))
    return file_name
