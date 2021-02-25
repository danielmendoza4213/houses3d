### 3D Houses3

### Objective:

From an address (in Flanders) obtain a 3d model of the property.

### About the Proyect:

This project uses images obtained from Geopunt.be that were prepared with the lidar method. Lidar is a method used to produce maps, in this case, these images have been used to obtain information about the height of buildings. Once the heights of a geographical area are obtained, they are plotted in 3D.

The code can be found in 3DHouses.py

### What do we need to plot in 3D

First we need to transform an address into geographic coordinates, then find what is the shape of the property and then find only the height data for the property area.
Once the height data is obtained, we can plot the surface of the property.

In order to do the above, we need python packages that request information directly from a database (API), packages that manipulate geographic information in the form of images and matrices, and also packages for plotting.

### Example

![Getting Started](Images\plot3d_example.png)

### Pending things to do:

Find a way to access maps without having to download them.

Plot other information about the houses, such as diameter, area or other characteristics.
