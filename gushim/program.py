import logging
import logging.config
import os
import sys
import yaml



sys.path.insert(0, 'opentaba-gushim-prj')
import opentaba_gushim_prj.gushim.mapi_service as mapi
import opentaba_gushim_prj.gushim.compress as compress
import opentaba_gushim_prj.gushim.GeoUtils as utils

gushim_url ='https://data.gov.il/dataset/3ef36ec6-f0e3-447b-bc9d-9ab4b3cee783/resource/f7a10a68-fba5-430b-ac11-970611904034/download/subgushall-nodes.zip'


def setup_logging(default_path='logging.yaml',default_level=logging.INFO,env_key='LOG_CFG'):
    """
    Setup logging configuration
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
    logger = logging.getLogger(__name__)
    return logger


def main():
    # LOG_CFG = my_logging.yaml    python    my_server.py
    logger = setup_logging()
    # logging.config.fileConfig('logging.conf')
    # logger = logging.getLogger("GushimApp")

    logger.info("Program started")
    # print_header()
    folder = get_or_create_workspace_folder()

    # file_name = mapi.get_gushim(folder, gushim_url)
    # compress.zip_uncompress(file_name, folder)

    csv_loc_file = r'C:\Users\sephi\github\opentaba-gushim\opentaba_gushim_prj\gushim\workspace\subgushall-nodes\sub_gush_all-nodes.csv'
    # utils.load_csv_into_json(csv_loc_file)
    utils.csv_to_geojson(csv_loc_file)

    # display_cats(folder)


def get_or_create_workspace_folder():
    base_folder = os.path.abspath(os.path.dirname(__file__))
    folder = 'workspace'
    full_path = os.path.join(base_folder, folder)

    if not os.path.exists(full_path) or not os.path.isdir(full_path):
        print('Creating new directory at {}'.format(full_path))
        os.mkdir(full_path)

    return full_path


# def download_gushim(folder, url):
#     return


if __name__ == '__main__':
    main()
