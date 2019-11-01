import gdal
from osgeo import gdal_array
import shapefile
import os
from timeit import default_timer as timer

from PIL import Image, ImageDraw

class CHANGE(object):

    def image_to_array(self,image):
        """
        将一个Python图像库的数组转换为一个gdal_array图片
        """
        image_array = gdal_array.numpy.frombuffer(image.tobytes(), 'b')
        image_array.shape = image.im.size[1], image.im.size[0]
        return image_array

    def world_to_pixel(self,geomatrix, x, y):
        """
        使用GDAL库的geomatrix对象((gdal.GetGeoTransform()))计算地理坐标的像素位置
        """
        ulx = geomatrix[0]
        uly = geomatrix[3]
        x_dist = geomatrix[1]
        pixel = int((x - ulx) / x_dist)
        line = int((uly - y) / x_dist)
        return pixel, line

def controller_for_clip(work_dir,input_tif,input_shp,output_tif):
    #work_dir 裁剪功能工作目录，定义这个后可基于此调用相对路径
    #input_tif 用于裁剪的Tif数据的相对路径
    #input_shp 用于裁剪的栅格shp数据的相对路径
    #output_tif 输出Tif数据
    #下面是一个例子

    os.chdir(work_dir)
    run=CHANGE()

    # 用于裁剪的栅格数据
    raster = input_tif
    # 用于裁剪的多边形shp文件
    shp = input_shp
    # 裁剪后的栅格数据
    output = output_tif

    src_array = gdal_array.LoadFile(raster)
    # 同时载入gdal库的图片从而获取geotransform
    src_image = gdal.Open(raster)
    geo_trans = src_image.GetGeoTransform()

    # 使用PyShp库打开shp文件
    r = shapefile.Reader("{}.shp".format(shp))

    # 将图层扩展转换为图片像素坐标
    min_x, min_y, max_x, max_y = r.bbox
    ul_x, ul_y = run.world_to_pixel(geo_trans, min_x, max_y)
    lr_x, lr_y = run.world_to_pixel(geo_trans, max_x, min_y)
    # 计算新图片的尺寸
    px_width = int(lr_x - ul_x)
    px_height = int(lr_y - ul_y)

    clip = src_array[:, ul_y:lr_y, ul_x:lr_x]
    # 为图片创建一个新的geomatrix对象以便附加地理参照数据
    geo_trans = list(geo_trans)
    geo_trans[0] = min_x
    geo_trans[3] = max_y
    # 在一个空白的8字节黑白掩膜图片上把点映射为像元绘制市县
    # 边界线
    pixels = []
    for p in r.shape(0).points:
        pixels.append(run.world_to_pixel(geo_trans, p[0], p[1]))
    raster_poly = Image.new("L", (px_width, px_height), 1)
    # 使用PIL创建一个空白图片用于绘制多边形
    rasterize = ImageDraw.Draw(raster_poly)
    rasterize.polygon(pixels, 0)
    # 使用PIL图片转换为Numpy掩膜数组
    mask = run.image_to_array(raster_poly)
    # 根据掩膜图层对图像进行裁剪
    clip = gdal_array.numpy.choose(mask, (clip, 0)).astype(gdal_array.numpy.float)
    # 将裁剪结果保存为tiff文件
    gdal_array.SaveArray(clip, "{}.tif".format(output),
                         format="GTiff", prototype=raster)


