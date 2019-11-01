from mosaic import controller_for_mosaic 
if __name__ == "__main__":
    input_tif_list = []
    input_tif_list.append('taihu/mosaic/0407RVUB2-3-4-8.tif')
    input_tif_list.append('taihu/mosaic/0407RVVB2-3-4-8.tif')
    input_tif_list.append('taihu/mosaic/0425RUUB2-3-4-8.tif')
    input_tif_list.append('taihu/mosaic/0425RUVB2-3-4-8.tif')
    controller_for_mosaic('/opt/amyz_test',  input_tif_list,'taihu/mosaic/merge8.tif')
