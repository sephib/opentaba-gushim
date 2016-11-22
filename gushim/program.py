import logging
import logging.config
import os
import sys
import yaml


sys.path.insert(0, 'opentaba-gushim-prj')
import opentaba_gushim_prj.gushim.mapi_service as mapi
import opentaba_gushim_prj.gushim.compress as compress
import opentaba_gushim_prj.gushim.GeoUtils as GeoUtils

gushim_url ='https://data.gov.il/dataset/3ef36ec6-f0e3-447b-bc9d-9ab4b3cee783/resource/f7a10a68-fba5-430b-ac11-970611904034/download/subgushall-nodes.zip'


def setup_logging(default_path='logging.yaml', default_level=logging.INFO, env_key='LOG_CFG'):
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


def get_mapi_uncompress_node_file(folder_path, mapi_format: str):
    for (dirpath, dirnames, filenames) in os.walk(folder_path):
        csv_files = [os.path.join(dirpath, fi) for fi in filenames if fi.endswith(mapi_format)]
    return csv_files


def main():
    logger = setup_logging(default_level=logging.DEBUG)
    logger.info("Program started")

    folder = get_or_create_workspace_folder()

    file_name = mapi.get_gushim(folder, gushim_url)
    # file_name = r'opentaba_gushim_prj/gushim/workspace/file_download.zip'
    compress.zip_uncompress(file_name, folder)
    csv_node_file = get_mapi_uncompress_node_file(folder, 'nodes.csv')

    GeoUtils.csv_to_geojson(csv_node_file[0])

    #Generate Topojson (reuse)
    #Push to GIT



def get_or_create_workspace_folder():
    base_folder = os.path.abspath(os.path.dirname(__file__))
    folder = 'workspace'
    full_path = os.path.join(base_folder, folder)

    if not os.path.exists(full_path) or not os.path.isdir(full_path):
        print('Creating new directory at {}'.format(full_path))
        os.mkdir(full_path)

    return full_path



if __name__ == '__main__':
    main()
