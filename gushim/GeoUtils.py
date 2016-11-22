import gdal
import logging
import dataconverters.commas as commas
import csv

# C:\OSGeo4W64\bin\ogr2ogr -f GeoJSON output.geojson input.vrt
# ogrinfo sub_gush_nodes.csv -dialect SQLite -sql "SELECT shapeid, MakePolygon(MakePoint(CAST(x AS float),CAST(y AS float))) FROM sub_gush_nodes GROUP BY shapeid"

# C:\Users\sephi\github\opentaba-gushim\opentaba_gushim_prj\gushim\workspace\subgushall-nodes>C:\OSGeo4W64\bin\ogrinfo sub_gush_nodes.csv -dialect SQLite -sql "SELECT MakePoint(CAST(x AS float),CAST(y AS float)) FROM sub_gush_nodes limit 5"
#
# C:\OSGeo4W64\bin\ogr2ogr -f GeoJSON temp.geojson sub_gush_nodes.csv -s_srs EPSG:2039 -t_srs EPSG:4326 -dialect SQLite -sql "SELECT MakePoint(CAST(x AS float),CAST(y AS float)) FROM sub_gush_nodes limit 5"
#
# C:\OSGeo4W64\bin\ogr2ogr -f GeoJSON temp.geojson sub_gush_nodes.csv -s_srs EPSG:2039 -t_srs EPSG:4326 -dialect SQLite -sql "SELECT shapeid, MakeLine(MakePoint(CAST(x AS float),CAST(y AS float))) FROM sub_gush_nodes GROUP BY shapeid limit 5"
#
#C:\OSGeo4W64\bin\ogr2ogr -f GeoJSON temp.geojson sub_gush_nodes.csv -s_srs EPSG:2039 -t_srs EPSG:4326 -dialect SQLite -sql "SELECT shapeid, MakePolygon(MakeLine(MakePoint(CAST(x AS float),CAST(y AS float)))) FROM sub_gush_nodes GROUP BY shapeid"

def csv_to_geojson(file_name):
    # Read in raw data from csv
    rawData = csv.reader(open(file_name, 'r'), dialect='excel')

    # the template. where data from the csv will be formatted to geojson
    template = \
        ''' \
        { "type" : "Feature",
            "id" : %s,
                "geometry" : {
                    "type" : "Point",
                    "coordinates" : ["%s","%s"]}
            },
        '''

    # the head of the geojson file
    output = \
        ''' \
    { "type" : "Feature Collection",
        {"features" : [
        '''

    # loop through the csv by row skipping the first
    iter = 0
    for row in rawData:
        iter += 1
        if iter >= 2:
            id = row[0]
            lat = row[1]
            lon = row[2]
            output += template % (row[0], row[2], row[1])

    # the tail of the geojson file
    output += \
        ''' \
        ]
    }
        '''

    # opens an geoJSON file to write the output to
    outFileHandle = open("output.geojson", "w")
    outFileHandle.write(output)
    outFileHandle.close()

def load_csv_into_json(full_path_file_name):
    with open(full_path_file_name, 'rb') as f:
        # records is an iterator over the records
        # metadata is a dict containing a fields key which is a list of the fields
        records, metadata = commas.parse(f)
        print(metadata)
        print(r for r in records)



