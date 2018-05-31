import datetime
import logging as lg
import pandas as pd
import geopandas as gp
from shapely.geometry import Polygon
import os
from io import open as io_open
from git import Repo
from pathlib import Path

from gushim import mapi_service
from gushim import utilities  # from .utilities import *
from gushim import gushimconfig
from gushim import geo_utils


def main():
    utilities.config(log_console=True, log_file=True )
    logger = utilities.get_logger(level=lg.DEBUG)
    datetime_str = datetime.datetime.utcnow().strftime('%Y%m%d_%H%M')

    logger.info("Program started")

    base_folder = os.path.abspath(os.path.dirname(__file__))
    path_to_folder = os.path.join(base_folder, gushimconfig.WORKSPACE_FOLDER)
    workspace_folder = utilities.get_or_create_folder(path_to_folder)
    path_to_folder = os.path.join(base_folder, gushimconfig.EXPORT_FOLDER)
    export_folder = utilities.get_or_create_folder(path_to_folder)
    logger.debug('The workspace folder is: {0}'.format(workspace_folder))

    repo = Repo(gushimconfig.REPO_DIR)
    if gushimconfig.NEW_BRANCH:
        origin = repo.create_remote(datetime_str, repo.remotes.origin.url)
        repo.create_head(datetime_str, origin.refs.master)

    if not gushimconfig.LOAD_SHAPEFILE:
        # Load Yeshuvim m.ask data into pandas
        path_to_file = os.path.join(base_folder, gushimconfig.YESHUV_MASK_FILE)
        df_yeshuv = pd.read_csv(path_to_file, header=0, encoding='utf-8-sig', index_col=False)
        logger.info('Successfully loaded yeshuv file {0} into pandas'.format(gushimconfig.YESHUV_MASK_FILE))

        # Download file from MAPI
        mapi_zip_file = Path(gushimconfig.WORKSPACE_FOLDER) / gushimconfig.GUSHIM_ZIP_FILE
        if not mapi_zip_file.exists():
            mapi_zip_file = mapi_service.get_gushim(workspace_folder, gushimconfig.GUSHIM_URL)

        utilities.zip_uncompress(mapi_zip_file)
        logger.debug('Successfully uncompressed file: {0}'.format(mapi_zip_file))


        # Load attribute data into geopandas
        csv_att_file = mapi_service.get_mapi_uncompress_file(workspace_folder, gushimconfig.END_ATTRIBUTE_FILE)
        path_to_file = os.path.join(workspace_folder, csv_att_file)
        df_att = pd.read_csv(path_to_file, header=0, encoding='utf-8-sig', index_col=False)
        logger.info('Successfully loaded attribute file {0} into pandas'.format(csv_att_file))

        # Join DataFrames
        merged_mask = pd.merge(left=df_att, right=df_yeshuv, how='inner', left_on='LOCALITY_I', right_on='ID')

        # Load node data into Geopandas
        csv_node_file = mapi_service.get_mapi_uncompress_file(workspace_folder, gushimconfig.END_NODE_FILE)
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
        gushim_shp = Path(base_folder) / gushimconfig.SHAPEFILE_PATH
        df_polygon_att_wgs = gp.read_file(str(gushim_shp.absolute()))
        logger.info('Shapefile {} loaded into GeoPandas'.format(gushimconfig.SHAPEFILE_PATH))

    if gushimconfig.SAVE_GUSHIM_SHAPEFILE:
        # timestr = time.strftime("%Y%m%d_%H%M%S")
        export_file = Path(base_folder, export_folder, 'Gushim{0}.shp'.format(datetime_str))
        df_polygon_att_wgs.to_file(export_file.absolute(), encoding="utf-8")
        logger.info('Successfully saved shapefile {0}'.format(export_file))

    # Get list of localities
    localities = df_polygon_att_wgs.groupby(['EngName']).size().index.tolist()
    # Prepare dataframe with relevant topojson column
    df_polygon_att_wgs['Name'] = df_polygon_att_wgs['GUSH_NUM']  # df_local.rename(columns={'GUSH_NUM': 'name'}, inplace=True)

    # gushimfiles each locality as geojson
    for local in localities:
        df_local = df_polygon_att_wgs[(df_polygon_att_wgs.EngName == local) & (df_polygon_att_wgs.Pop2015 > gushimconfig.MIN_POPULATION)]
        if not df_local.empty:
            file_name_string = utilities.slugify(local) #remove unsafe characters
            try:
                export_file = Path(base_folder, export_folder, '{0}.geojson'.format(file_name_string))
                if gushimconfig.EXPORT_TO_GEOJSON:
                    local_geojson = df_local.to_json()
                    with io_open(export_file, 'w', encoding='utf-8') as f:
                        f.write(local_geojson)
                    # with io_open(export_file, 'w', encoding='utf-8') as f:
                    #     df_local.to_json(f, force_ascii=False)
                if gushimconfig.EXPORT_TO_TOPOJSON:
                    export_temp_geojson_file = os.path.join(base_folder, export_folder, 'temp_json4{0}.geojson'.format(file_name_string))
                    local_geojson = df_local[['Name', 'geometry']].to_json()  # local_topojson = df_local.to_json()
                    # if not os.path.exists(export_file) or not os.path.isdir(export_file):
                    with open(export_temp_geojson_file, 'w') as f:
                        f.write(local_geojson)
                    # filename, _ = os.path.splitext(export_temp_geojson_file)
                    topojson_file = os.path.join(base_folder, export_folder, '{0}.topojson'.format(file_name_string))
                    geo_utils.geoson_to_topojson(export_temp_geojson_file, topojson_file)

                    try:
                        os.remove(export_temp_geojson_file)
                        logger.debug('Successfully deleted temp_geojson file: {0}'.format(export_temp_geojson_file))
                    except OSError as e:
                        print ("Error: {} - {}.".format(e.message, e.strerror))

            except OSError as e:
                print ("Error: {} - {}.".format(e.message, e.strerror))
                logger.warning('failed to save geojson for: {0}'.format(local))
    logger.debug('Finished to saved files to GeoJSON')

    if gushimconfig.EXPORT_ALL_GUSHIM:
        all_gushim_file = os.path.join(base_folder, export_folder, '{0}.geojson'.format('ISRAEL_GUSHIM'))
        all_local_json = df_polygon_att_wgs.to_json()
        with open(all_gushim_file, 'w') as f:
            f.write(all_local_json)
        filename, _ = os.path.splitext(all_gushim_file)
        topojson_file = filename + '.topojson'
        geo_utils.geoson_to_topojson(all_gushim_file, topojson_file)
        # TODO zip geojson file and delete the original geojson files since it is too big

    # TODO convert to function taking dfpg and crs

    logger.info('Successfully  created  Polygon in geopandas')

    # geojson_file = r'C:\Users\sephi\github\opentaba_gushim\opentaba_gushim_prj\gushim\workspace\subgushall-nodes\countries.geo.json'
    # geojson_file = r'C:\Users\sephi\github\opentaba_gushim\opentaba_gushim_prj\gushim\workspace\abugosh.geoson'
    #
    #Generate Topojson (reuse)

    # Log Statistics
    logger.info('Number of Localities to be exported is {0}'.format(len(localities)))
    logger.info('Number of Gushim / Polygons that have been exported {0}'.format(len(df_polygon_att_wgs.shapeid)))
    logger.debug('Number of Gushim per Localities is {0}'.format(df_polygon_att_wgs.groupby(['EngName'])['GUSH_NUM'].size()))

    # TODO Push to GIT
    if gushimconfig.PUSH_TO_GITHUB:
        repo = Repo(gushimconfig.REPO_DIR)
        topojson_files = [i for i in repo.untracked_files if i.endswith('topojson')]
        repo.index.add(topojson_files)
        repo.index.commit('Files created on {0}'.format(datetime_str))
        remote_origin = repo.remote('origin')
        remote_origin.push(repo.active_branch.name)
        logger.info('Files where pushed to GitHub repo')
        logger.debug('The following files were pushed to the repo {0}'.format(topojson_files))


    logger.info("Program completed")


if __name__ == '__main__':
    main()
