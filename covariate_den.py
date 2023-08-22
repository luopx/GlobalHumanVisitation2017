'''
This code calculated covariates with a suffix of _den, taking road1_den as an example.
'''

import os
import glob
import arcpy
from arcpy import env
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

# Set environment settings
env.workspace = "..."
env.overwriteOutput = True
env.parallelProcessingFactor = 0
arcpy.CheckOutExtension("Spatial")

# road tif path list
class_code = '1'
road_tif_path='.../road_'+class_code+'.tif'

# all fishnet path
select_fpath_df=pd.read_csv(r"...")
select_fpath_list=select_fpath_df['path'].values.tolist()

# all fishnet csv path
fcsv_path_list=glob.glob(r'...\*')

# save folder
out_savefolder='...'
dbf_savefolder = out_savefolder + 'dbf/'
csv_savefolder = out_savefolder + 'csv/'
results_savefolder = out_savefolder + 'results/'

# main function
def subnationZonalStatistic(input_fishnet):

    try:

        fishnet_name = input_fishnet.split('\\')[-1][15:]  # '9_1'

        cur_dbf_savefolder=dbf_savefolder+'road_'+class_code+'/'
        cur_csv_savefolder = csv_savefolder + 'road_' + class_code + '/'
        cur_results_savefolder = results_savefolder + 'road_' + class_code + '/'
        if not os.path.exists(cur_dbf_savefolder):
            os.makedirs(cur_dbf_savefolder)
        if not os.path.exists(cur_csv_savefolder):
            os.makedirs(cur_csv_savefolder)
        if not os.path.exists(cur_results_savefolder):
            os.makedirs(cur_results_savefolder)

        # assign zonal statistics tif value to fishnet
        dbf_path = cur_dbf_savefolder + fishnet_name + '.dbf'
        outZSaT = arcpy.gp.ZonalStatisticsAsTable_sa(input_fishnet, "FID", road_tif_path, dbf_path, "DATA", "MAXIMUM")

        # convert dbf to csv
        arcpy.TableToTable_conversion(dbf_path, cur_csv_savefolder, fishnet_name + '.csv')

        # corresponding fishnet csv
        fcsv = [x for x in fcsv_path_list if x.split('\\')[-1].split('.')[0] == fishnet_name][0]
        f_df = pd.read_csv(fcsv)
        f_df = f_df[['FID', 'gridid','AREA_GEO']]

        # zonal statistics csv
        zs_df = pd.read_csv(cur_csv_savefolder + fishnet_name + '.csv')
        zs_df = zs_df[['FID_', 'COUNT']]
        zs_df.columns = ['FID', 'COUNT']

        # merge
        f_df = pd.merge(f_df, zs_df, how='left', on='FID')

        # fill NAN with 0
        f_df['COUNT'] = f_df['COUNT'].fillna(0)

        # calculate road density
        covariate_name='road'+class_code+'_den'  # 'road1_den'
        f_df[covariate_name]=f_df['COUNT']/f_df['AREA_GEO']
        f_df=f_df[['FID','gridid',covariate_name]]

        # save
        f_df.to_csv(cur_results_savefolder + fishnet_name + '.csv', index=False, header=True)

    except:

        print(input_fishnet)


for ee in select_fpath_list:
    subnationZonalStatistic(ee)