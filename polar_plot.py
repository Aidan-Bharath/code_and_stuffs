from __future__ import division
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas.tools.plotting import *
from mpl_toolkits.mplot3d import Axes3D
import datetime as dt
import matplotlib.dates as dt
from multiprocessing import Pool

def load_panel(a):
    a = pd.read_pickle(a)
    return a

def magnitude(a):
    a = np.sqrt(a['u']**2+a['v']**2+a['w']**2)
    return a

def depth_avg(a):
    if len(a.shape) == 3:
        a = a.loc[['u','v','w'],time[0]:time[1]].mean(axis=2)
        a = a.reindex(index=a.index.to_datetime())
        return a
    else:
        a[time[0]:time[1]].mean(axis=1)
        a = a.reindex(index=a.index.to_datetime())
        return a

def reindex(a):
    a = a.reindex(index=a.index.to_datetime())
    return a

def sample_std(a):
    a = a.resample(sample,how='std')
    return a

def sample_mean(a):
    a = a.resample(sample,how='mean')
    return a


def tke(a):
    q = np.sqrt((1/3)*(a['u']**2+a['v']**2+a['w']**2))
    return q

def polar_plot(panel):
    theta_p1 = np.arctan2(panel[2]['v'],panel[2]['u'])
    theta_adcp = np.arctan2(panel[0]['v'],panel[0]['u'])
    panel = Pool().map(magnitude,panel)
    print panel

    ax1 = plt.subplot(121, polar=True)
    #sc = ax1.scatter(theta_p1, panel[2], c = panel[3],s=50,cmap=cm.jet ,edgecolor='none',label = 'Probe')
    #ax1.scatter(theta_adcp, panel[0], c = panel[1] ,s=50,cmap=cm.jet ,edgecolor='none',marker='^',label = 'ADCP')
    #ax1.grid(True)
    #plt.legend()
    #cbar = plt.colorbar(sc)
    #cbar.set_label(r'Standard Deviation over 5 minutes')
    #ax1.set_xticklabels(['E', 'NE','N','NW','W', 'SW', 'S', 'SE'])
    #ax1.set_title("June BPb Velocities and Direction", va='bottom')

    ax2 = plt.subplot(122)
    '''
    ax2.plot_date(adcp.index.to_datetime(),adcp['v'],'-',label='ADCP Northern Velocity')
    ax2.plot_date(p1.index.to_datetime(),p1['v'],'-',label='Probe Northern Velocity')
    ax2.plot_date(adcp.index.to_datetime(),adcp['u'],'-',label='ADCP Eastern Velocity')
    ax2.plot_date(p1.index.to_datetime(),p1['u'],'-',label='Probe Eastern Velocity')
    ax2.xaxis.set_minor_locator(dt.HourLocator(byhour=range(24), interval=1))
    ax2.xaxis.set_minor_formatter(dt.DateFormatter('%H:%M\n%a,%d'))
    ax2.xaxis.grid(True, which="minor")
    ax2.yaxis.grid()
    ax2.xaxis.set_major_locator(dt.MonthLocator())
    ax2.xaxis.set_major_formatter(dt.DateFormatter('\n\n\n%b\n%Y'))
    plt.legend()
    plt.tight_layout()
    ax2.set_ylabel('Velocity (m/s)')
    plt.title('Velocities')
    '''
    panel[0].plot()
    panel[2].plot()
    plt.show()


if __name__ == "__main__":

    global time,sample
    time = ['2013-06-21 09:00:00','2013-06-21 15:00:00']
    sample = '5T'

    adcp = '/home/aidan/thesis/probe_data/panels/2013/june_july/GP-130620-BPb_vel'
    adcps = '/home/aidan/thesis/probe_data/panels/2013/june_july/GP-130620-BPb_stats'
    p1 = '/home/aidan/thesis/probe_data/panels/2013/june_july/GP-130621-24_BPb_p-int'
    panels = [adcp,adcps,p1]

    #Load Panels
    panels = Pool().map(load_panel,panels)

    #depth averaged
    panels = Pool().map(depth_avg,panels)

    #Reindex
    a = panels[0].reindex(index=panels[0].index.to_datetime()).resample(sample)
    b = panels[1].reindex(index=panels[1].index.to_datetime()).resample(sample)
    c = panels[2].reindex(index=panels[2].index.to_datetime()).resample(sample)
    d = panels[2].reindex(index=panels[2].index.to_datetime()).resample(sample,how='std')
    panels = [a,b,c,d]

    polar_plot(panels)
