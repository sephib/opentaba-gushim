import logging
import logging.config
import pandas as pd
import geopandas as gp
import numpy as np
from shapely.geometry import Point, Polygon, LineString
import time
import os
import sys
import yaml

sys.path.insert(0, 'opentaba-gushim-prj')
import gushim.mapi_service as mapi
import gushim.compress as compress
import gushim.geo_utils as geo_utils
import gushim.utilities as util

gushim_url ='https://data.gov.il/dataset/3ef36ec6-f0e3-447b-bc9d-9ab4b3cee783/resource/f7a10a68-fba5-430b-ac11-970611904034/download/subgushall-nodes.zip'

# CONFIG
END_NODE_FILE = 'nodes.csv'
END_ATTRIBUTE_FILE = 'attributes01.csv'
YESHUV_MASK_FILE = r'support_data/Yeshuvim2015.csv'
MIN_POPULATION = 2000
SAVE_GUSHIM_SHAPEFILE = True  #save the gushim to shapefile
EXPORT_TO_GEOJSON = True
EXPORT_TO_TOPOJSON = True  #Save also to TopoJSON
EXPORT_ALL_GUSHIM = True
DELETE_GEOJSON = False
WORKSPACE_FOLDER = 'workspace'
EXPORT_FOLDER = 'export'
LOAD_SHAPEFILE = True


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


def get_mapi_uncompress_file(folder_path, mapi_format):
    """
    :param folder_path: Location of the unzip file
    :param mapi_format: The file format of the gushim unzipped file - currently csv
    :return: return filename
    """
    for (dirpath, dirnames, filenames) in os.walk(folder_path):
        csv_files = [os.path.join(dirpath, fi) for fi in filenames if fi.endswith(mapi_format)][0]

    return csv_files


def get_or_create_folder(folder_name):
    base_folder = os.path.abspath(os.path.dirname(__file__))
    if not folder_name:
        folder_name = 'workspace'
    full_path = os.path.join(base_folder, folder_name)

    if not os.path.exists(full_path) or not os.path.isdir(full_path):
        print('Creating new directory at {}'.format(full_path))
        os.mkdir(full_path)

    return full_path


def main():
    logger = setup_logging(default_level=logging.DEBUG)
    logger.info("Program started")

    workspace_folder = get_or_create_folder(WORKSPACE_FOLDER)
    export_folder = get_or_create_folder(EXPORT_FOLDER)
    logger.debug('The workspace folder is: {0}'.format(workspace_folder))

    base_folder = os.path.abspath(os.path.dirname(__file__))

    if not LOAD_SHAPEFILE:
        # Load Yeshuvim mask data into pandas
        path_to_file = os.path.join(base_folder, YESHUV_MASK_FILE)
        df_yeshuv = pd.read_csv(path_to_file, header=0, encoding='utf-8-sig', index_col=False)
        logger.info('Successfully loaded yeshuv file {0} into pandas'.format(YESHUV_MASK_FILE))

        # Download file from MAPI
        # file_name = mapi.get_gushim(workspace_folder, gushim_url)  #include copy
        # # file_name = r'opentaba_gushim_prj/gushim/workspace/file_download.zip'
        # compress.zip_uncompress(file_name, workspace_folder)
        # logger.debug('Successfully uncompressed file: {0}'.format(file_name))

        # Load attribute data into geopandas
        csv_att_file = get_mapi_uncompress_file(workspace_folder, END_ATTRIBUTE_FILE)
        path_to_file = os.path.join(workspace_folder, csv_att_file)
        df_att = pd.read_csv(path_to_file, header=0, encoding='utf-8-sig', index_col=False)
        logger.info('Successfully loaded attribute file {0} into pandas'.format(csv_att_file))

        # Join DataFrames
        merged_mask = pd.merge(left=df_att, right=df_yeshuv, how='inner', left_on='LOCALITY_I', right_on='ID')

        # Load node data into Geopandas
        csv_node_file = get_mapi_uncompress_file(workspace_folder, END_NODE_FILE)
        path_to_file = os.path.join(workspace_folder, csv_node_file)
        df_node = pd.read_csv(path_to_file, skiprows=1, names=['shapeid', 'x', 'y'], encoding='utf-8-sig')
        # geojson_file = geo_utils.csv_to_geojson(csv_node_file[0]) OLD METHOD to generate GeoJSON - Need to Add Projection
        logger.info('Successfully loaded node file {0} into pandas'.format(csv_node_file))

        df_node['geometry'] = df_node.apply(lambda x: (x['x'], x['y']), axis=1)
        logger.info('Successfully created  point coordinates in dataframe ')

        df_point = df_node.groupby('shapeid')['geometry'].apply(lambda x: Polygon(x.tolist())).reset_index()
        # df_node['geometry'] = df_node.groupby('shapeid').apply(lambda x: Polygon(x.tolist([Point(xy) for xy in zip(x.x, x.y)]))).reset_index()

        df_polygon = gp.GeoDataFrame(df_point, geometry='geometry')
        df_polygon.crs = {'init': 'epsg:2039'}
        logger.debug('Successfully created  Polygon object in GeoDataframe ')

        # Join DataFrames
        merged_inner = pd.merge(left=merged_mask, right=df_polygon, how='inner', left_on='shapeid', right_on='shapeid')
        logger.debug('Successfully merged dataframe')
        logger.debug(type(merged_inner))

        # Create GeoDataFrame polygon
        df_polygon_att = gp.GeoDataFrame(merged_inner, geometry='geometry')
        df_polygon_att.crs = {'init': 'epsg:2039'}  #define GeoDataFrame
        logger.debug('Successfully created GeoDataframe ITM')
        df_polygon_att_wgs = df_polygon_att.to_crs({'init': 'epsg:4326'}).copy()
        logger.info('Successfully projected file GeoDataframe to WGS84')
    else:
        shapefile_path = r'C:\Users\sephi\github\opentaba_gushim\opentaba_gushim_prj\gushim\export\Gushim20170209_173107.shp'
        df_polygon_att_wgs = gp.read_file(shapefile_path)
        logger.info('Shapefile {} loaded into GeoPandas'.format(shapefile_path ))

    # Get list of localities
    localities = df_polygon_att_wgs.groupby(['EngName']).size().index.tolist()

    # export each locality as geojson
    for local in localities:
        df_local = df_polygon_att_wgs[(df_polygon_att_wgs.EngName == local) & (df_polygon_att_wgs.Pop2015 > MIN_POPULATION)]
        if not df_local.empty:
            file_name_string = "".join(x for x in local if x.isalnum()).encode('utf-8').upper()  #remove unsafe characters
            print (file_name_string)
            try:
                export_file = os.path.join(base_folder, export_folder, '{0}.geojson'.format(file_name_string))
                local_geojson = df_local.to_json()
                if EXPORT_TO_GEOJSON:
                    with open(export_file, 'w') as f:
                        f.write(local_geojson)
                if EXPORT_TO_TOPOJSON:
                    export_temp_geojson_file = os.path.join(base_folder, export_folder, 'topo4{0}.geojson'.format(file_name_string))
                    df_local.rename(columns={'GUSH_NUM': 'name'}, inplace=True)
                    # local_topojson = df_local['name'].to_json()
                    local_topojson = df_local.to_json()
                    # if not os.path.exists(export_file) or not os.path.isdir(export_file):
                    with open(export_temp_geojson_file, 'w') as f:
                        f.write(local_topojson)
                    # filename, _ = os.path.splitext(export_temp_geojson_file)
                    topojson_file = '{}.topojson'.format(file_name_string)
                    print("Geojson: {}, Topojson: {} ".format(export_temp_geojson_file, topojson_file))
                    geo_utils.geoson_to_topojson(export_temp_geojson_file, topojson_file)
                    try:
                        os.remove(export_temp_geojson_file)
                    except OSError, e:
                        print ("Error: {} - {}.".format(e.message, e.strerror))
                if DELETE_GEOJSON:
                    try:
                        os.remove(export_file)
                    except OSError, e:
                        print ("Error: {} - {}.".format(e.message, e.strerror))
            except OSError, e:
                print ("Error: {} - {}.".format(e.message, e.strerror))
                logger.warning('failed to save geojson for: {0}'.format(local))
    logger.debug('Finished to saved files to GeoJSON')

    if EXPORT_ALL_GUSHIM:
        all_gushim_file = os.path.join(base_folder, export_folder, '{0}.geojson'.format('israel_gushim'))
        all_local_json = df_polygon_att_wgs.to_json()
        with open(all_gushim_file, 'w') as f:
            f.write(all_local_json)
        filename, _ = os.path.splitext(all_gushim_file)
        topojson_file = filename + '.topojson'
        geo_utils.geoson_to_topojson(all_gushim_file, topojson_file)

    # TODO convert to function taking dfpg and crs

    if SAVE_GUSHIM_SHAPEFILE:
        timestr = time.strftime("%Y%m%d_%H%M%S")
        export_file = os.path.join(base_folder, export_folder, 'Gushim{0}.shp'.format(timestr))
        df_polygon_att_wgs.to_file(export_file)
        logger.info('Successfully saved shapefile {0}'.format(export_file))


    logger.info('Successfully  created  Polygon in geopandas')

    # geojson_file = r'C:\Users\sephi\github\opentaba_gushim\opentaba_gushim_prj\gushim\workspace\subgushall-nodes\countries.geo.json'
    # geojson_file = r'C:\Users\sephi\github\opentaba_gushim\opentaba_gushim_prj\gushim\workspace\abugosh.geoson'
    #
    #Generate Topojson (reuse)

    # Log Statistics
    logger.info('Number of Localities to be exported is {0}'.format(len(localities)))
    logger.info('Number of Gushim / Polygons that have been exported {0}'.format(len(df_polygon_att_wgs.shapeid)))
    logger.debug('Number of Gushim per Localitis is {0}'.format(df_polygon_att_wgs.groupby(['HebName'])['GUSH_NUM'].size()))

    # TODO Push to GIT

    logger.info("Program completed")





if __name__ == '__main__':
    main()
