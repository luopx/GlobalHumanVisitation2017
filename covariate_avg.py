'''
This code calculated covariates with a suffix of _avg, taking tem_avg as an example.
'''

import glob
import arcpy
from arcpy import env
from arcpy.sa import *
import pandas as pd

# Set environment settings
env.workspace = '...'
env.overwriteOutput = True
env.parallelProcessingFactor = 0
arcpy.CheckOutExtension("Spatial")

# temperature tif path
tif_path='avg_temperature_resample.tif'

# all fishnet path
select_fpath_df=pd.read_csv('...')
select_fpath_list=select_fpath_df['path'].values.tolist()

# all fishnet csv path
fcsv_path_list=glob.glob('...\*')

# save folder
out_savefolder='...'
zs_tif_savefolder=out_savefolder+'zonal_statistics_tif/'
empty1_savefolder=out_savefolder+'empty1_tif/'
nibble_savefolder=out_savefolder+'nibbled_tif/'
fill_savefolder=out_savefolder+'fill_tif/'
dbf_savefolder=out_savefolder+'dbf/'
csv_savefolder=out_savefolder+'csv/'
gridid_savefolder=out_savefolder+'csv_AddGridid/'


def subnationZonalStatistic(input_fishnet):

    fishnet_name=input_fishnet.split('\\')[-1][15:] # '143_19'

    try:
        # generate zonal statistic tif
        snap_raster='...'+fishnet_name+'.tif'
        arcpy.env.snapRaster = snap_raster
        zs_tif_path=zs_tif_savefolder + fishnet_name + '.tif'
        arcpy.gp.ZonalStatistics_sa(snap_raster,"Value",tif_path,zs_tif_path, "MEAN", "DATA")

        # nibble
        empty1=Con((IsNull(zs_tif_path)) & (~IsNull(snap_raster)),zs_tif_path,1)
        empty1_tif_path=empty1_savefolder+ fishnet_name + '.tif'
        empty1.save(empty1_tif_path)
        nibble_tif_path=nibble_savefolder+fishnet_name + '.tif'
        arcpy.gp.Nibble_sa(zs_tif_path,empty1_tif_path,nibble_tif_path,"DATA_ONLY","PROCESS_NODATA","")

        # fill empty after nibble
        filled=Con((IsNull(nibble_tif_path)) & (~IsNull(snap_raster)),FocalStatistics(nibble_tif_path, NbrRectangle(100, 100, "CELL"), "MEAN"), nibble_tif_path)
        filled_tif_path=fill_savefolder+fishnet_name+'.tif'
        filled.save(filled_tif_path)

        # assign zonal statistics tif value to fishnet
        dbf_path=dbf_savefolder+fishnet_name+'.dbf'
        outZSaT = arcpy.gp.ZonalStatisticsAsTable_sa(input_fishnet,"FID",filled_tif_path,dbf_path,"DATA","MEAN")

        # convert dbf to csv
        arcpy.TableToTable_conversion(dbf_path, csv_savefolder, fishnet_name + '.csv')

        # add gridid
        fcsv = [x for x in fcsv_path_list if x.split('\\')[-1][:-4] == fishnet_name][0]
        f_df = pd.read_csv(fcsv)
        f_df = f_df[['FID', 'gridid']]
        zs_df = pd.read_csv(csv_savefolder + fishnet_name + '.csv')
        zs_df = zs_df[['FID_', 'MEAN']]
        zs_df.columns = ['FID', 'tem_avg']
        f_df = pd.merge(f_df, zs_df, how='left', on='FID')
        f_df.to_csv(gridid_savefolder + fishnet_name + '.csv', index=False, header=True)
    except:
        print(input_fishnet)

for cur_each in select_fpath_list:
    subnationZonalStatistic(cur_each)