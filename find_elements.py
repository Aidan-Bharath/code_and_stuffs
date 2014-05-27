import  numpy as np
from datatools import node_finder


if __name__ == "__main__":

    neiDir = '/home/aidan/thesis/grids/dngrid_final.nei'
    grdDir = '/home/aidan/thesis/grids/dngrid_grd.dat'
    fileDir = '/home/aidan/thesis/ncdata/gp/2014/dngrid_0001.nc'

    start,stop = [-66.3413,44.2654],[-66.3331,44.2682]
    lonlat = np.array([start,stop])
    element,node = node_finder(lonlat,neiDir,grdDir)
    print element
