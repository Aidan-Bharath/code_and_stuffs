from __future__ import division
import numpy as np
import sys
import matplotlib
import netCDF4 as net
from datetime import datetime
from datetime import timedelta
import matplotlib.pyplot as plt
import matplotlib.tri as Tri
import matplotlib.ticker as ticker



if __name__ == "__main__":

    GPBPb = [-66.3391,44.2761]
    fileDir = '/home/aidan/thesis/ncdata/gp/2014/'
    filename = 'dngrid_0001.nc'
    nc = net.Dataset(fileDir+filename).variables
    t_slice = ['2014-02-02T06:40:00','2014-02-02T07:05:00']
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


    lat = nc['lat'][:]
    lon = nc['lon'][:]
    h = nc['h'][:]
    zeta = nc['zeta'][argtime,:]+h[None,:]
    nv = nc['nv'][:].T-1
    siglay = nc['siglay'][:]
    z = zeta[:,None,:]*siglay[None,:,:]
    dep = np.zeros([argtime.shape[0],siglay.shape[0],nv.shape[0]])
    for i in range(z.shape[0]):
        for j in range(nv.shape[0]):
            el = (z[i,:,nv[j,0]]+z[i,:,nv[j,1]]+z[i,:,nv[j,2]])/3
            dep[i,:,j] = el

    bot_lvl = 4
    top_lvl = 1

    ut,ub = nc['u'][argtime,top_lvl,:],nc['u'][argtime,bot_lvl,:]
    vt,vb = nc['v'][argtime,top_lvl,:],nc['v'][argtime,bot_lvl,:]
    wt,wb = nc['ww'][argtime,top_lvl,:],nc['ww'][argtime,bot_lvl,:]


    velt = np.sqrt(ut[:]**2+vt[:]**2+wt[:]**2)
    velb = np.sqrt(ub[:]**2+vb[:]**2+wb[:]**2)
    vel = velt - velb
    #topl = np.argwhere((vel[:,top_lvl,:] < vel[:,bot_lvl,:])).flatten()
    #vel[:,:,topl] = 0

    levels = np.arange(-40,5,1)
    vmax = 0.8
    vmin = -0.8

    matplotlib.rcParams['contour.negative_linestyle'] = 'solid'
    for i in range(vel.shape[0]):
        grid =  Tri.Triangulation(lon,lat,triangles=nv)
        fig = plt.figure()
        plt.rc('font',size='22')
        ax = fig.add_subplot(111,aspect=(1.0/np.cos(np.mean(lat)*np.pi/180.0)))
        CS = ax.tricontour(grid, -h,levels=levels,shading='faceted',cmap=plt.cm.gist_earth)
        #ax.clabel(CS, fontsize=9, inline=1,colors='k',fmt='%1d')
        f = ax.tripcolor(grid, vel[i,:],vmax=vmax,vmin=vmin,cmap=plt.cm.PuOr)
        frame = plt.gca().patch.set_facecolor('0.5')
        cbar = fig.colorbar(f,ax=ax)
        cbar.set_label(r'Layer Velocity Difference $(m/s)$', rotation=-90,labelpad=30)
        plt.scatter(GPBPb[0],GPBPb[1],s=200,color='black')
        #plt.title(str(time[j]))
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.grid()
        scale = 1
        ticks = ticker.FuncFormatter(lambda lon, pos: '{0:g}'.format(lon/scale))
        ax.xaxis.set_major_formatter(ticks)
        ax.yaxis.set_major_formatter(ticks)
        ax.set_xlim([-66.380025,-66.310543])
        ax.set_ylim([44.232371,44.290312])
        plt.show()


