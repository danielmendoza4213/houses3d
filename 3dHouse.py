"""packages to request the addres and geometries of the house from 
the public database of the flemish goverment"""
import requests
import json

"""packages to manipulate tif files and read raster data"""
import rasterio as rio
import rioxarray as rxr

"""packages to plot  the elevation of the house in 1d"""
import matplotlib.pyplot as plt
import earthpy.plot as ep
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns

"""packages to plot the elevation of the house in 3d"""
import plotly.graph_objects as go

"""packages to handle dataframes, arrays and zipped files"""
import numpy as np
import pandas as pd
import zipfile


""" Imput area """
street = input("Enter street ")
number = input("Enter house number ")
post = input("Enter postal code ")

print(street, number, post)

""" Create an empty list to store the polygone of the house"""
polygone = []


""" Function to request the coordinates and the shape of the property. 
    To request the desired information, the api ask for the ID of the building. 
    Search for an address, use the address id to find the id of the unit building; use the previous id to find the building id 
    The building id section has the polygone, which is the shape of the building"""


def house_info(street, number, post):
    a = requests.get(
        "https://api.basisregisters.dev-vlaanderen.be/v1/adressen?"
        + "straatnaam="
        + street
        + "&huisnummer="
        + number
        + "&postcode="
        + post
        + "&limit=1"
    )
    b = a.json()
    id1 = b["adressen"][0]["identificator"]["objectId"]
    print("Address found: Id1 is", id1)
    c = requests.get(
        "https://api.basisregisters.vlaanderen.be/v1/gebouweenheden?adresObjectId="
        + id1
    )
    d = c.json()
    id2 = d["gebouweenheden"][0]["identificator"]["objectId"]
    print("Building units found: Id2 is", id2)
    e = requests.get(
        "https://api.basisregisters.vlaanderen.be/v1/gebouweenheden/" + id2
    )
    f = e.json()
    id3 = f["gebouw"]["objectId"]
    print("Building found: Id3 is", id3)
    g = requests.get("https://api.basisregisters.vlaanderen.be/v1/gebouwen/" + id3)
    h = g.json()
    poly = h["geometriePolygoon"]["polygon"]["coordinates"][0]
    polygone.append(poly)


"""Run Function to obtain house shape and coordinates"""

house_info(street, number, post)

""" coordiantes use to identify the right file"""

x = polygone[0][0][0]
y = polygone[0][0][1]

""" tthere are two csv files in the directory, for DMS and DMT, both files show the extension of each tif file.
     We will use this csv to select the tiff file to analyze."""
dtm_df = pd.read_csv("dtm_info.csv")
dtm_df.set_index("file", inplace=True)

dsm_df = pd.read_csv("dsm_info.csv")
dsm_df.set_index("file", inplace=True)

"""here the tiff file is selected, both for DSM and DMT according to X and Y coordinates (obtained with the house_info function)  """

file_dsm_selected = dsm_df.loc[
    (x < dsm_df.xmax) & (x > dsm_df.xmin) & (y < dsm_df.ymax) & (y > dsm_df.ymin)
]

dsm_selected = file_dsm_selected.index.format()[0]

file_dtm_selected = dtm_df.loc[
    (x < dtm_df.xmax) & (x > dtm_df.xmin) & (y < dtm_df.ymax) & (y > dtm_df.ymin)
]
dtm_selected = file_dtm_selected.index.format()[0]

print("DTM selected:", dtm_selected)
print("DSM selected:", dsm_selected)


""" Code to download the specific DMT and DSM from the database, the files can be downloaded zipped using the base_url_(see below)
    and adding the name of the file, wich is taken from the csv file and adding  a .zip ending """

post_link_dtm = dtm_selected.split(".")[0] + ".zip"
post_link_dsm = dsm_selected.split(".")[0] + ".zip"

base_url_dtm = (
    "https://downloadagiv.blob.core.windows.net/dhm-vlaanderen-ii-dtm-raster-1m/"
)
base_url_dsm = (
    "https://downloadagiv.blob.core.windows.net/dhm-vlaanderen-ii-dsm-raster-1m/"
)
""" now we have a extact url for the desire tif file"""
url_dtm = base_url_dtm + post_link_dtm
url_dsm = base_url_dsm + post_link_dsm

""" function to download the file"""
""" for DTM"""


def download_dtm(url_dtm):
    filename = url_dtm.split("/")[-1]
    r = requests.get(url_dtm, stream=True)
    if r.ok:
        with open(filename, "wb") as file:
            for chunk in r.iter_content(1024 * 100):
                file.write(chunk)
    else:
        print("error")


"""for DMS"""


def download_dsm(url_dsm):
    filename = url_dsm.split("/")[-1]
    r = requests.get(url_dsm, stream=True)
    if r.ok:
        with open(filename, "wb") as file:
            for chunk in r.iter_content(1024 * 100):
                file.write(chunk)
    else:
        print("error")


"""Run both previous functions"""
download_dtm(url_dtm)
download_dsm(url_dsm)

"""Once both files are downloaded ( it will take some time),we need to unzip the tif files,
     they will be stored in the folder GeoTiff"""

targetdtm = url_dtm.split("/")[-1]
targetdsm = url_dsm.split("/")[-1]

handledtm = zipfile.ZipFile(targetdtm)
handledsm = zipfile.ZipFile(targetdsm)

handledtm.extract("GeoTIFF/" + dtm_selected)
handledsm.extract("GeoTIFF/" + dsm_selected)

""" With the desired file, we will read the tif file as an array and at the same time we will clip the shape of the property.
    The shape of the property comes from the house_info function (request api). Clipping meeans that the code will only
    read the selected shape of the building but this shape need to be inside a list called geometries"""

geometries = [{"type": "Polygon", "coordinates": polygone}]

read_dsm = rxr.open_rasterio("GeoTIFF/" + dsm_selected).rio.clip(
    geometries, from_disk=True
)
read_dtm = rxr.open_rasterio("GeoTIFF/" + dtm_selected).rio.clip(
    geometries, from_disk=True
)

""" with both DSM and DTM as array, we create the canopy height model, to only show the heights of buildings and other structures"""
canopy = read_dsm - read_dtm
""" rasteriza of the canopy, to save the area selected as tif"""
canopy.rio.to_raster("clipped.tif")
""" read the canpy file"""
with rio.open("clipped.tif") as img:
    chm = img.read(1)
"""plot 1d the selected ares + hillshade to look at it better """
fig, ax = plt.subplots(figsize=(10, 6))
ep.plot_bands(
    chm, ax=ax, cmap="terrain", title="Overlay Hillshade & CHM",
)
ax.imshow(chm, cmap="Greys", alpha=0.5)
plt.show()
""" plot the elevations """
z = chm
sh_0, sh_1 = z.shape
x, y = np.linspace(0, 1, sh_0), np.linspace(0, 1, sh_1)
fig = go.Figure(data=[go.Surface(z=z, x=x, y=y)])
fig.update_layout(
    title="House",
    autosize=False,
    width=500,
    height=500,
    margin=dict(l=65, r=50, b=65, t=90),
)
fig.show()

"""building information"""

print("Altitude:", np.amax(z), "m")
print("Coordinates:", polygone[0][0][0], ",", polygone[0][0][1])
