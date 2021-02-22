import os
import requests
import rasterio as rio
import rioxarray as rxr
import pandas as pd


""" Prepare files
    1. Make a dataframe with the bounds per tif file, so que can use a loc mehtod to select only 
    the desired file"""


""" 1.A: Files for DSM"""
dsm_files = os.listdir("DSM")
dsm_bounds_lst = []
for lst in dsm_files:
    file = rxr.open_rasterio("DSM/" + lst, masked=True).squeeze()
    dsm_bounds = file.rio.bounds()
    dsm_bounds_lst.append(
        [lst, dsm_bounds[0], dsm_bounds[1], dsm_bounds[2], dsm_bounds[3]]
    )

dsm_df = pd.DataFrame(dsm_bounds_lst, columns=["file", "xmin", "ymin", "xmax", "ymax"])

dsm_df.set_index("file", inplace=True)

""" 1.B: Files for DTM"""
dtm_files = os.listdir("DTM")
dtm_bounds_lst = []
for lst in dtm_files:
    file = rxr.open_rasterio("DTM/" + lst, masked=True).squeeze()
    dtm_bounds = file.rio.bounds()
    dtm_bounds_lst.append(
        [lst, dtm_bounds[0], dtm_bounds[1], dtm_bounds[2], dtm_bounds[3]]
    )

dtm_df = pd.DataFrame(dtm_bounds_lst, columns=["file", "xmin", "ymin", "xmax", "ymax"])

dtm_df.set_index("file", inplace=True)

""" Take the 2 df to houses.py 
    1.dsm_df
    2.dtm_df
    """

