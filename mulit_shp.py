import os
import fiona
import zipfile
import shutil
from shapely.geometry import Polygon, mapping, Point, MultiPoint, MultiPolygon


def download_shpfile(shp_type, shp_name, shp_coordinates):
    """下载shp文件

    Args:
        shp_type： String类型，Point或者Polygon
        shp_name: String类型，shp文件名字
        shp_coordinates: Array类型，经纬度信息

    Returns:
        url：shp文件下载地址
        code:
            0: 成功
            1：coordinates格式错误
            2: 经纬度参数错误
            3: 压缩失败
            4: 下载失败
            5: 删除文件失败

    """
    shp_path = "/tmp"
    lon_max = 180
    lon_min = -180
    lat_max = 90
    lat_min = -90

    compressed_shp_path = os.path.join(shp_path, shp_name)
    target_dir = ''.join((compressed_shp_path, '.zip'))
    src_dirs = [compressed_shp_path, target_dir]
    if os.path.exists(compressed_shp_path):
        flag1 = delete_file(src_dirs)
        if not flag1:
            message = "delete source file error"
            return False, 5, message
    schema = {'geometry': shp_type,
              'properties': {}}
    crs = {'proj': 'longlat', 'ellps': 'WGS84', 'datum': 'WGS84',
           'no_defs': True}
    compressed_path = os.path.join(compressed_shp_path, 'layers')
    os.makedirs(compressed_path)
    name = ''.join((shp_type, '.shp'))
    path = os.path.join(compressed_path, name)
    with fiona.open(path, mode='w', driver='ESRI Shapefile',
                    schema=schema, crs=crs, encoding='utf-8') as layer:
        points = list()
        if shp_type == "Point":
            for shp_coordinate in shp_coordinates:
                p1 = float(shp_coordinate[0])
                p2 = float(shp_coordinate[1])
                point = Point([p1, p2])
                # 将Point对象转为GeoJSON格式
                point = mapping(point)
                feature = {'geometry': point,
                           'properties': {}}
                # 写入文件
                layer.write(feature)
        elif shp_type == "Polygon":

            for shp_coordinate in shp_coordinates:
                points.clear()

                for point in shp_coordinate:
                    f3 = float(point[0])
                    f4 = float(point[1])
                    if not (
                            lon_min <= f3 <= lon_max and lat_min <= f4 <= lat_max):
                        message = "Parameter value error"
                        return False, 2, message
                    points.append([f3, f4])

                polygon = Polygon(points)
                polygon = mapping(polygon)
                feature = {'geometry': polygon,
                           'properties': {}}
                layer.write(feature)

    result = compression_shp(compressed_shp_path, target_dir)
    if not result:
        return False, 3, "compression error"


def compression_shp(src_dir, target_dir):
    """压缩shp文件

    Args:
        src_dir: string类型，源路径，需要压缩的文件路径
        target_dir：string类型，目标路径，压缩到哪个路径下

    Returns:

    """
    try:
        filelist = []
        if os.path.isfile(src_dir):
            filelist.append(src_dir)
        else:
            for root, dirs, files in os.walk(src_dir):
                for name in files:
                    filelist.append(os.path.join(root, name))
        zf = zipfile.ZipFile(target_dir, "w", zipfile.zlib.DEFLATED)
        for tar in filelist:
            arcname = tar[len(src_dir):]
            zf.write(tar, arcname)

        zf.close()
        return True
    except Exception as ex:
        print(ex)
        return False


def delete_file(src_dirs):
    """删除文件和文件下的子目录所有内容

    Args:
        src_dir: Array类型，需要删除的文件路径

    Returns:

    """
    try:
        for src_dir in src_dirs:
            if os.path.exists(src_dir):
                if os.path.isdir(src_dir):
                    shutil.rmtree(src_dir)
                else:
                    os.remove(src_dir)
        return True
    except Exception as ex:
        print(ex)
        return False


if __name__ == '__main__':
    shp_type = "Polygon"
    shp_name = "test"

    shp_coordinates = [[[20, 30], [30, 30], [30, 40], [20, 40] ],[ [30, 40], [40, 40], [40, 50], [30, 50] ]]


    download_shpfile(shp_type, shp_name, shp_coordinates)
