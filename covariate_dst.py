'''
This code calculated covariates with a suffix of _dst, taking poi1_dst as an example.
'''

import glob
import pandas as pd
import numpy as np
from math import radians
from sklearn.neighbors import BallTree

# all fishnet csv path
fsv_path_list=glob.glob(r'...\*.csv')

# read lc_arr
lc_arr_path = r"...\poi_1.npy"
lc_arr = np.load(lc_arr_path)

# Create tree from the candidate points
tree = BallTree(lc_arr, leaf_size=40, metric='haversine')

# savefolder
savefolder='...'

# main function
def shortestDst(fsv_path):

    try:
        # read fishnet table
        fishnet_df = pd.read_csv(fsv_path)
        fishnet_df = fishnet_df[['FID','gridid','CENTROID_X', 'CENTROID_Y']]

        # transform degree to radians
        fishnet_arr = np.array(fishnet_df.apply(lambda xx: [radians(xx['CENTROID_Y']), radians(xx['CENTROID_X'])], axis=1).to_list())

        # Find closest points and distances
        distances, indices = tree.query(fishnet_arr, k=1)
        # Transpose to get distances and indices into arrays
        distances = distances.transpose()
        closest_dist = distances[0]

        # add distance to result dataframe and transform to km
        covaritae_name='poi1_dst'
        fishnet_df[covaritae_name]=closest_dist
        fishnet_df[covaritae_name]=fishnet_df[covaritae_name].map(lambda aa:aa*6371000/1000)
        fishnet_df=fishnet_df[['FID','gridid',covaritae_name]]

        # save
        savename=fsv_path.split('\\')[-1]
        savepath=savefolder+savename
        fishnet_df.to_csv(savepath,index=False,header=True)
    except:
        print(fsv_path)


for ee in fsv_path_list:
    shortestDst(ee)