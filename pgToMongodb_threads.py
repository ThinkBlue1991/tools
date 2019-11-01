import os
import random
import re
import json
import datetime

import psycopg2.pool
from pymongo import MongoClient
from bson import json_util
from common import parse_config
from s3_server.s3_controller import upload_object
import multiprocessing
from threading import Thread

database = "postgres"
user = "postgres"
password = "123456"
host = "192.168.4.32"
port = 5432
max_conn = 200
min_conn = 5
table = "image_meta_tmp"
limit_size = 100
simple_conn_pool = psycopg2.pool.SimpleConnectionPool(min_conn, max_conn,
                                                      database=database,
                                                      user=user,
                                                      password=password,
                                                      host=host, port=port)
db_url = 'mongodb://192.168.4.32:27017/'
db_name = 'metadata'
col_metadata = 'sat_image'
max_pool_size = 1000

client = MongoClient(db_url, maxPoolSize=max_pool_size)
db = client[db_name]
collection = db[col_metadata]

from math import cos, pi, radians
from shapely.geometry import Polygon


earth_radius = 6371.173 


def get_area(geometry):
    area_list = list()
    if geometry['type'] == "Polygon":
        points_list = geometry['coordinates']
        for points in points_list:
            xy_coordinates = switch_to_xy_coordinates(points)
            polygon = Polygon(xy_coordinates)
            area_list.append(polygon.area)
    else:
        area_list.append(0)

    return area_list


def switch_to_xy_coordinates(points):

    lat_dist = pi * earth_radius / 180.0

    longitudes, latitudes = zip(*points)
    y = (lat * lat_dist for lat in latitudes)
    x = (lon * lat_dist * cos(radians(lat)) for lat, lon in
         zip(latitudes, longitudes))
    return list(zip(x, y))


def find_place(start, limit):
    try:
        conn = simple_conn_pool.getconn()
        cursor = conn.cursor()
        query = "SELECT satellite_id,sensor_id,ST_AsGeoJSON(\"geo\"),start_time,file_name,icon from image_meta_tmp limit %d offset %d" % (limit, start)
        cursor.execute(query)
        print(query)
        results = cursor.fetchall()

        count = start
        metadata_list = list()
        for result in results:
            count = count + 1
            print("=========%d===========" % (count))
            satellite_id = result[0]
            sensor_id = result[1]
            geo = result[2]
            start_time = result[3]
            file_name = result[4]
            icon = result[5]

            image_path = os.path.join(icon, file_name).replace(
                '\\', '/')
            if os.path.exists(image_path):
                if upload_object('metadatabucket', file_name, image_path):
                    metadata = dict()
                    metadata['satelliteId'] = satellite_id
                    metadata['sensorId'] = sensor_id
                    metadata['geometry'] = json.loads(geo)
                    metadata['area'] = get_area(metadata['geometry'])[0] 
                    metadata['receiveTime'] = start_time
                    metadata['cloudPercent'] = random.randint(0, 90)
                    metadata['solarZenith'] = random.randint(0, 100)
                    metadata['source'] = 0
                    metadata['imageGsd'] = 10
                    metadata['flag'] = -1
                    metadata['thumbFileLocation'] = "GF1_PMS1_E120.5_N36.4_20181030_L1A0003559539/GF1_PMS1_E120.5_N36.4_20181030_L1A0003559539-MSS1_thumb.jpg"
                    metadata['xmlFileLocation'] = "GF1_PMS1_E120.5_N36.4_20181030_L1A0003559539/GF1_PMS1_E120.5_N36.4_20181030_L1A0003559539-MSS1.xml"
                    #metadata['browseFileLocation'] = image_path
                    metadata['browseFileLocation'] = file_name
                    metadata[
                        'tiffFileLocation'] = 'GF1_PMS1_E120.5_N36.4_20181030_L1A0003559539/GF1_PMS1_E120.5_N36.4_20181030_L1A0003559539-MSS1.tiff'

                    metadata_list.append(metadata)

        if len(metadata_list) < 1000:
            collection.insert_many(metadata_list)
        else:
            loop_count = int(len(metadata_list) / 1000)
            index = 0
            for i in range(0, loop_count):
                print('==============index=%d==========' % index)
                collection.insert_many(metadata_list[index:index + 1000])
                index += 1000

            end = len(metadata_list) - (index+1000)
            if end > 0:
                collection.insert_many(metadata_list[index+1000:])

    except Exception as ex:
        print("777")
        print(ex)
        message = "Server error"
        return False, 2, message
    finally:
        cursor.close()
        simple_conn_pool.putconn(conn, close=False)


if __name__ == "__main__":
    limit = 1000

    p = list()
    count = 0 
    for i in range(0, 40):
        t = Thread(target=find_place, args=(count, limit))
        p.append(t)
        count = count + limit

    for i in range(0, 40):
        p[i].start()

    for i in range(0, 40):
        p[i].join()

    print("All done")


