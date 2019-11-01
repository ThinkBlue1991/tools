import gdal_merge as gm
import os
#拼接感兴趣区多幅影像(两幅两幅拼)
def controller_for_mosaic(work_dir, input_tif_list, output_tif):
    #work_dir 拼接功能工作目录，定义这个后可以基于此调用相对路径
    #input_tif_list 输入的tif数据，List类型
    #output_tif 输出拼接后的tif数据
    #示例：
    #input_tif_list = []
    #input_tif_list.append('taihu/mosaic/0407RVUB2-3-4-8.tif')
    #input_tif_list.append('taihu/mosaic/0407RVVB2-3-4-8.tif')
    #controller_for_mosaic('/opt/amyz_test',  input_tif_list,'taihu/mosaic/merge5.tif')
    #以上示例为在/opt/amyz_test工作目录下，拼接taihu/mosaic/0407RVUB2-3-4-8.tif与taihu/mosaic/0407RVVB2-3-4-8.tif
    #生成taihu/mosaic/merge5.tif数据

    os.chdir(work_dir)
    input_all_list=[];
    input_all_list.append('')
    input_all_list.append('-o')
    input_all_list.append(output_tif)

    for input_tif in input_tif_list:
        input_all_list.append(input_tif)
    gm.main(input_all_list)

