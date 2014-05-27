from __future__ import division
import numpy as np
import pandas as pd
from multiprocessing import Pool
from matplotlib import pyplot as plt

def load_panel(a):
    a = pd.read_pickle(a)
    return a

def time_index(a):
    a = a.reindex(index=a.index.to_datetime())
    return a

def resamp(a):
    a = a.resample('10T')
    return a

def magnitude(a):
    mag = np.sqrt(a['u']**2+a['v']**2+a['w']**2)
    return mag

def std(a):
    a = a.resample('10T',how='std')
    return a


if __name__ == "__main__":

    f0 = '/home/aidan/thesis/probe_data/panels/2013/june_july/GP-130621-BPb-hr'
    f1 = '/home/aidan/thesis/probe_data/panels/2013/june_july/GP-130621-24-BPb_sigmas'
    el = '/home/aidan/thesis/probe_data/panels/2013/june_july/GP-130621-24-BPb_els'

    el = pd.read_pickle(el)
    el = el.reindex(index=el.index.to_datetime())
    el = el.resample('10T')

    f = [f0,f1]

    f = Pool().map(load_panel,f)
    bins = f[0].minor_axis[:].values
    sigma = np.array([0.98999,0.94999,0.86999,0.74999,0.58999,0.41000,0.25000,0.13000,0.05000,0.01000])
    f = Pool().map(magnitude,f)
    f = Pool().map(time_index,f)
    f1 = f[1].shift(-20,freq='T')
    f = [f[0],f1]
    d = Pool().map(resamp,f)
    s = Pool().map(std,f)
    print d

    time = '2013-06-21 14:50:00'
    d = [d[0].loc[time],d[1].loc[time]]
    s = [s[0].loc[time],s[1].loc[time]]
    el = el.loc[time]
    d[0][20.61:] = np.nan
    sigma = sigma*el.values
    rms = 0.26
    width = '4'

    fig,ax = plt.subplots()
    plt.rc('font',size='22')
    ax.errorbar(d[1].values, el[::-1],linewidth=width, xerr=s[1],label='FVCOM')
    ax.set_ylim([0,np.ceil(np.max(el))])#.values)])
    ax.grid(True)
    ax.set_ylabel(r'FVCOM Elevation $(m)$')
    ax.set_xlabel(r'Velocity $(m/s)$')
    ax.legend(loc=3,fontsize='18')
    ax1 = ax.twinx()
    ax1.errorbar(d[0], bins, xerr=s[0],linewidth=width,color='red',label='ADCP')
    ax1.set_ylim([0,np.ceil(np.max(el))])#.values)])
    ax1.set_ylabel(r'ADCP Elevation $(m)$')
    ax1.legend(loc=2,fontsize='18')
    plt.show()

