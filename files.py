import os
import requests
import rasterio as rio
import rioxarray as rxr
import pandas as pd


""" Prepare files
    1. Make file belgium.csv a dataframe, so we can use a loc method to get the cooridantes
    2. Make a dataframe with the bounds per tiff file, so que can use a loc mehtod to select only 
    the desired file"""


""" 1. """
belgium = pd.read_csv("belgium.csv")

""" 2.A: Files for DSM"""
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

""" 2.B: Files for DTM"""
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

""" Take the 3 df to houses.py 
    1.belgium
    2.dsm_df
    3.dtm_df
    """

