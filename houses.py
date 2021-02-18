import pandas as pd

from files import belgium
from files import dsm_df
from files import dtm_df

from pyproj import Transformer


import rioxarray as rxr
import rasterio as rio
from rasterio.windows import from_bounds
import geopandas as gpd


""" plot"""
import matplotlib.pyplot as plt
import earthpy.plot as ep
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
import seaborn as sns


""" Write the address to look foor """
NUMBER = "14"
STREET = "Kerkstraat"
CITY = "Kapellen"
POSTCODE = 2950

"""__________________________________ """

address_selected = belgium.loc[
    (belgium.NUMBER == NUMBER)
    & (belgium.STREET == STREET)
    & (belgium.CITY == CITY)
    & (belgium.POSTCODE == POSTCODE)
]

""" coordinates x and y """

bel_x = address_selected["LAT"].values[0]
bel_y = address_selected["LON"].values[0]


"""tranform coordates X,Y"""
transformer = Transformer.from_crs(4326, 31370)

x, y = transformer.transform(bel_x, bel_y)


""" select tiff file to look for"""

"""DSM"""
file_dsm_selected = dsm_df.loc[
    (x < dsm_df.xmax) & (x > dsm_df.xmin) & (y < dsm_df.ymax) & (y > dsm_df.ymin)
]

dsm_selected = file_dsm_selected.index.format()[0]

"""DTM"""
file_dtm_selected = dtm_df.loc[
    (x < dtm_df.xmax) & (x > dtm_df.xmin) & (y < dtm_df.ymax) & (y > dtm_df.ymin)
]
dtm_selected = file_dtm_selected.index.format()[0]


print("The DMS selected is:", dsm_selected)
print("The DTM selected is:", dtm_selected)

""" Canpy from the DMS and DTM selected"""
read_dsm = rxr.open_rasterio("DSM/" + dsm_selected, masked=True).squeeze()
read_dtm = rxr.open_rasterio("DTM/" + dtm_selected, masked=True).squeeze()

print("Is the spatial extent the same?", read_dsm.rio.bounds() == read_dtm.rio.bounds())

print(
    "Is the resolution the same?",
    read_dsm.rio.resolution() == read_dtm.rio.resolution(),
)

chm = read_dsm - read_dtm
chm.rio.to_raster("chm.tif")

""" read section around the coordinates"""
x_left = x - 50
x_right = x + 25
y_up = y + 100
y_down = y - 25

with rio.open("chm.tif") as img:
    chm = img.read(1, window=from_bounds(x_left, y_down, x_right, y_up, img.transform))

""" plot area 1d"""

fig, ax = plt.subplots(figsize=(10, 6))
ep.plot_bands(
    chm, ax=ax, cmap="terrain", title="Overlay Hillshade & DSM",
)
ax.imshow(chm, cmap="Greys", alpha=0.5)
plt.show()

""" plot area 3d """

chm_gdp = gpd.GeoDataFrame(chm)

df = chm_gdp.unstack().reset_index()
df.columns = ["X", "Y", "Z"]
df["X"] = pd.Categorical(df["X"])
df["X"] = df["X"].cat.codes
fig = plt.figure(figsize=(35, 10))
ax = fig.gca(projection="3d")
ax.plot_trisurf(df["Y"], df["X"], df["Z"], cmap=plt.cm.viridis, linewidth=0.1)
ax.view_init(20, -230)
plt.show()
