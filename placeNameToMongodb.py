import shapefile
from pymongo import MongoClient


db_url = 'mongodb://192.168.4.32:27017/'
db_name = 'metadata_place'
col_metadata = 'place_china'
max_pool_size = 1000

client = MongoClient(db_url, maxPoolSize=max_pool_size)
db = client[db_name]
collection = db[col_metadata]


def read_shp(shp_path):
    """ 读取shp文件的类型和点坐标信息

    Args:
        shp_path: shp文件的绝对路径

    Return:
        type: shp文件的类型
        coordinates: 图像的点坐标串,是一个二维数组形式。
    """
    try:
        # 读取shp文件
        file_shp = shapefile.Reader(shp_path)

        # 读取图像的类型
        # result = file_shp.load_shp(shp_path)
        # print(result)
        type_shp = file_shp.shapeTypeName.capitalize()
        # print(type_shp)
        # 读取shp图像的所有点坐标
        shapes = file_shp.shapes()
        geometry_list = list()
        for shape in shapes:
            geometry = dict()
            geometry['type'] = type_shp

            points_list = shape.points

            # 将tuple类型的点转成list
            coordinate = list()
            for points in points_list:
                coordinate.append(list(points))

            geometry['coordinates'] = [coordinate]

            geometry_list.append(geometry)
            # break

        return geometry_list
    except Exception as e:
        print(e)
        return False, None


def read_dbf(dbf_path):
    file_dbf = shapefile.Reader(dbf_path)

    records = file_dbf.records()
    areas = list()
    for record in records:
        area = ""
        record_dict = record.as_dict()
        if 'NAME_0' in record_dict:
            area = "中国"

        if 'NL_NAME_1' in record_dict and record_dict['NL_NAME_1'] != '':
            area = '|'.join((area, record_dict['NL_NAME_1'].split('|')[0]))

        if 'NL_NAME_2' in record_dict and record_dict['NL_NAME_2'] != '':

            area = '|'.join((area, record_dict['NL_NAME_2']))

        if 'NL_NAME_3' in record_dict and record_dict['NL_NAME_3'] != '':
            area = '|'.join((area, record_dict['NL_NAME_3']))
        # areas.append(records)
        areas.append(area)
        # break
    return areas


if __name__ == "__main__":
    shp_path = "E:\gadm36_CHN_shp\gadm36_CHN_1.shp"
    dbf_path = "E:\gadm36_CHN_shp\gadm36_CHN_1.dbf"
    shp_list = read_shp(shp_path)
    area_list = read_dbf(dbf_path)

    if len(shp_list) != 0:
        for i in range(0, len(shp_list)):
            place = dict()
            place['name'] = area_list[i]
            place['geometry'] = shp_list[i]
            collection.insert_one(place)