###################################################################################################
# Module: gushimconfig.py
# Description: Global defaults, can be configured by user by passing values to utils.config()
# License: MIT, see full license in LICENSE.txt
# Web: https://github.com/gboeing/osmnx
###################################################################################################

import logging as lg


# default locations to save data, logs, images, and cache
GUSHIM_URL ='https://data.gov.il/dataset/3ef36ec6-f0e3-447b-bc9d-9ab4b3cee783/resource/f7a10a68-fba5-430b-ac11-970611904034/download/subgushall-nodes.zip'
GUSHIM_ZIP_FILE = 'MapiGushim20180523_1750.zip'

# CONFIG
END_NODE_FILE = 'nodes.csv'
END_ATTRIBUTE_FILE = 'attributes01.csv'
YESHUV_MASK_FILE = r'../support_data/Yeshuvim2015.csv'
WORKSPACE_FOLDER = r'../workspace'
EXPORT_FOLDER = r'../gushimfiles'
MIN_POPULATION = 20000
LOAD_SHAPEFILE = True
SHAPEFILE_PATH = r'../gushimfiles/Gushim20180531_1112.shp'
SAVE_GUSHIM_SHAPEFILE = True  # Save the gushim to shapefile
EXPORT_TO_GEOJSON = True
EXPORT_TO_TOPOJSON = True  # Save to TopoJSON
EXPORT_ALL_GUSHIM = False
REPO_DIR = '../'
NEW_BRANCH = False
PUSH_TO_GITHUB = False


# write log to file and/or to console
log_file = False
log_console = False
log_level = lg.DEBUG
log_name = 'gushim'
log_filename = 'gushim'
log_folder = r'../logs'
