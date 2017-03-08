# from  gdal import ogr, osr
import logging as lg
# import dataconverters.commas as commas
import csv
import os
import subprocess
import sys
from topojson import topojson
from gushim import utilities

def csv_to_geojson(file_name, output_geojson=None):
    logger = logging.getLogger(__name__)

    # input_geojson_file = './opentaba_gushim_prj/gushim/workspace/input.vrt'
    # input_geojson_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'workspace', 'input.vrt')
    input_csv_file = file_name
    if not output_geojson:
        basename = os.path.basename(file_name)
        output_geojson = basename + '{0}'.format('.geoson')
        dirname = os.path.dirname(file_name)
        output_geojson = os.path.join(dirname, output_geojson)
    if os.path.isfile(output_geojson):
        os.remove(output_geojson)

    ogr_dir ='C:\\OSGeo4W64\\bin\\ogr2ogr'
    output_format = 'GeoJSON'
    s_srs = 'EPSG:2039'
    t_srs = 'EPSG:4326'
    sql_command = "SELECT shapeid, MakePolygon(MakeLine(MakePoint(CAST(x AS float),CAST(y AS float)))) FROM 'sub_gush_all-nodes' GROUP BY shapeid"
    subprocess_command = [ogr_dir, '-f', output_format,
                          output_geojson, input_csv_file,
                          '-s_srs', s_srs,
                          '-t_srs', t_srs,
                          '-dialect', 'sqlite',
                          '-sql', sql_command
                          ]
    logger.info('subprocess command to be run: {}'.format(subprocess_command))
    try:
        # in_ds = ogr.GetDriverByName("CSV").Open(file_name)
        # out_ds = gdal.ogr.GetDriverByName(output_format).CopyDataSource(in_ds, output_geojson)
        # print(type(out_ds))
        subprocess.call(subprocess_command)
        logger.info('successfully converted {0} into {1}'.format(file_name, output_geojson))
        return output_geojson
    except OSError as err:
        print("OS error: {0}".format(err))
    except ValueError:
        print("Could not convert data ")
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise

    # Read in raw data from csv
    # rawData = csv.reader(open(file_name, 'r'), dialect='excel')


def geoson_to_topojson(in_path, out_path, quantization=1e6, simplify=0.0001):
    # logger = logging.getLogger(__name__)
    logger = utilities.get_logger(level=lg.DEBUG)

    # give it a path in and out
    try:
        topojson(in_path, out_path, quantization, simplify)
        logger.info('Converted geojson into {0}'.format(out_path))
    except:
        raise



# def load_csv_into_json(full_path_file_name):
#     with open(full_path_file_name, 'rb') as f:
#         # records is an iterator over the records
#         # metadata is a dict containing a fields key which is a list of the fields
#         records, metadata = commas.parse(f)
#         print(metadata)
#         print(r for r in records)



