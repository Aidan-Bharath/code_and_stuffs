from __future__ import division
import numpy as np
import sys
import netCDF4 as net
from datetime import datetime
from datetime import timedelta
import matplotlib.pyplot as plt
import matplotlib.tri as Tri
import matplotlib.ticker as ticker


if __name__ == "__main__":

    fs3 = [-66.3421,44.2606]
    fs4 = [-66.3354,44.2605]
    fs5 = [-66.3381,44.2505]
    GPBPa = [-66.3395,44.2778]
    GPBPb = [-66.3391,44.2761]
    GPTA = [-66.3391,44.2799]
    GPTAJ = [-66.3380,44.2743]
    podlon = np.array([fs3[0],fs3[0],fs4[0],fs5[0],GPBPa[0],GPBPb[0],GPTA[0],GPTAJ[0]])
    podlat = np.array([fs3[1],fs3[1],fs4[1],fs5[1],GPBPa[1],GPBPb[1],GPTA[1],GPTAJ[1]])

    fileDir = '/home/aidan/thesis/ncdata/gp/2014/'
    filename = 'dngrid_0001.nc'
    nc = net.Dataset(fileDir+filename).variables

    t_slice = ['2014-02-02T11:40:00','2014-02-02T12:05:00']
    t_slice = np.array(t_slice,dtype='datetime64[us]')
    time = nc['time'][:]+678942
    time = np.array(time)
    t = time.shape[0]
    l = []
    for i in range(t):
        date = datetime.fromordinal(int(time[i]))+timedelta(days=time[i]%1)-timedelta(days=366)
        l.append(date)
    time = np.array(l,dtype='datetime64[us]')
    if t_slice.shape[0] != 1:
        argtime = np.argwhere((time>=t_slice[0])&(time<=t_slice[-1])).flatten()

    h = nc['h'][:]
    nbe = nc['nbe'][:]
    u = np.mean(nc['u'][argtime,:,:],axis=1)
    v = np.mean(nc['v'][argtime,:,:],axis=1)
    a2u = nc['a2u'][:]
    a1u = nc['a1u'][:]
    lat = nc['lat'][:]
    lon = nc['lon'][:]
    nv = nc['nv'][:].T-1

    clist = []
    for i in range(argtime.shape[0]):
        dudy=a2u[0,:]*u[0,:]+a2u[1,:]*u[i,nbe[0,:]-1]+a2u[2,:]*u[i,nbe[1,:]-1]+a2u[3,:]*u[i,nbe[2,:]-1]
        dvdx=a1u[0,:]*v[0,:]+a1u[1,:]*v[i,nbe[0,:]-1]+a1u[2,:]*v[i,nbe[1,:]-1]+a1u[3,:]*v[i,nbe[2,:]-1]
        curl = dvdx-dudy
        clist.append(curl)

    curl = np.array(clist)
    levels = np.arange(-36,5,2)
    vmax = 0.03
    vmin = -0.03

    for i in range(curl.shape[0]):
        grid =  Tri.Triangulation(lon,lat,triangles=nv)
        fig = plt.figure()
        plt.rc('font',size='22')
        ax = fig.add_subplot(111,aspect=(1.0/np.cos(np.mean(lat)*np.pi/180.0)))
        ax.tricontour(grid, -h,levels=levels,shading='faceted',cmap=plt.cm.gist_earth)
        #mask = []
        #for j in range(curl.shape[1]):
        #    if np.abs(curl[i,j]) >= 0.009:
        #        mask.append(False)
        #    else:
        #        mask.append(True)
        #grid1 =  Tri.Triangulation(lon,lat,triangles=nv,mask=mask)
        f = ax.tripcolor(grid, curl[i,:],vmax=vmax,vmin=vmin,cmap=plt.cm.RdBu)
        frame = plt.gca().patch.set_facecolor('0.5')
        cbar = fig.colorbar(f,ax=ax)
        #plt.scatter(podlon[1],podlat[1],s=200,color='black')
        #plt.scatter(podlon[2],podlat[2],s=200,color='black')
        plt.scatter(podlon[3],podlat[3],s=200,color='black')
        #plt.scatter(podlon[4],podlat[4],s=200,color='black')
        #plt.scatter(podlon[5],podlat[5],s=200,color='black')
        #plt.scatter(podlon[6],podlat[6],s=200,color='black')
        #plt.title(str(time[b[:]]))
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.grid()
        cbar.set_label(r'Vorticity $(1/s)$', rotation=-90,labelpad=30)
        scale = 1
        ticks = ticker.FuncFormatter(lambda lon, pos: '{0:g}'.format(lon/scale))
        ax.xaxis.set_major_formatter(ticks)
        ax.yaxis.set_major_formatter(ticks)
        ax.set_xlim([-66.370025,-66.310543])
        ax.set_ylim([44.242371,44.300312])
        plt.show()
