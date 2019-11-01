from math import cos, pi, radians
from shapely.geometry import Polygon


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
    earth_radius = 6371.173  # in km
    lat_dist = pi * earth_radius / 180.0

    longitudes, latitudes = zip(*points)
    y = (lat * lat_dist for lat in latitudes)
    x = (lon * lat_dist * cos(radians(lat)) for lat, lon in
         zip(latitudes, longitudes))
    return list(zip(x, y))


if __name__ == '__main__':
    # points = [[119.91248937, 31.54322250], [120.60921101, 31.54321196],
    #           [120.60925922, 30.95053625], [119.91254003, 30.95054643],
    #           [119.91248937, 31.54322250]]
    # points = switch_to_xy_coordinates(points)
    # polygon = Polygon(points)
    # # the area in square degrees
    # area_sdeg = polygon.area  # 平方公里
    # print(area_sdeg)

    shape = {"coordinates": [[[119.6449633789174, 31.91640979354078],
                               [120.28217041021134, 31.91640979354078],
                               [120.28217041021134, 31.603478771625973],
                               [119.6449633789174, 31.603478771625973],
                               [119.6449633789174, 31.91640979354078]]],
              "type": "Polygon"}

    print(get_area(shape))

