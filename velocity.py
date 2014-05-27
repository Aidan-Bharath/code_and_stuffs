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
    a = a.resample('3T')
    return a

def std(a):
    a = a.resample('3T',how='std')
    return a
def magnitude(a):
    mag = np.sqrt(a['u']**2+a['v']**2+a['w']**2)
    return mag

def theta(a):
    a = a.mean(axis=2)
    a = np.arctan2(a['v'],a['u'])
    return a


if __name__ == "__main__":

    '''
    This code plots the velocity timeseries and the squared difference between
    fvcom and adcp datasets. It also calculates the RMS error between ebb and
    flood tide velocities separately.
    '''

    # Directories for the panels of adcp and fvcom data.
    f0 = '/home/aidan/thesis/probe_data/panels/2012/flw_stn4_adcp_corrected'
    f1 = '/home/aidan/thesis/probe_data/panels/2012/GP-120727-FS4_sigma'
    f = [f0,f1]

    # sigma layer widths.
    sbin = np.array([0.02,0.06,0.1,0.14,0.18,0.18,0.14,0.1,0.06,0.02])

    # Load panels
    f = Pool().map(load_panel,f)

    # Calculate the angle of the flow based on u and v data. Tnorth adn south
    # flows carry the +/- sign.
    d = Pool().map(theta,f)

    # Calculate the Magnitude of the velocity.
    f = Pool().map(magnitude,f)

    # Reindex date index as datetime objoect for both angle and velocity
    # dataframes.
    f = Pool().map(time_index,f)
    d = Pool().map(time_index,d)

    # Time shift the FVCOM datasets.
    f1 = f[1].shift(-8,freq='T')
    d1 = d[1].shift(-8,freq='T')
    f = [f[0],f1]
    d = [d[0],d1]

    # Resample raw data for mean data.
    s = Pool().map(std,f)
    f = Pool().map(resamp,f)
    d = Pool().map(resamp,d)

    # Slice flood and ebb tide periods based on flow direction.
    da0,df0 = d[0][d[0]>0],d[1][d[1]>0]
    da1,df1 = d[0][d[0]<0],d[1][d[1]<0]

    # calculated the depth averages for both adcp and fvcom data. fvcom depth
    # average is done as a weighted average based on the sigma layer width.
    f0 = f[0].loc[f[1].index].mean(axis=1)
    f1 = pd.Series(np.sum(np.asarray(f[1])*sbin,axis=1),index=f[1].index)

    # And for standard deviation.

    s0 = s[0].loc[s[1].index].mean(axis=1)
    s1 = pd.Series(np.sum(np.asarray(s[1])*sbin,axis=1),index=s[1].index)
    s = [s0,s1]

    # Separate velocity data into ebb and flood tides, and consider speeds
    # greater than 'speed'.
    speed = 0.1
    a0,a1 = f0[da0.index],f1[df0.index]
    a0,a1 = a0[a0>speed],a1[a1>speed]
    b0,b1 = f0[da1.index],f1[df1.index]
    b0,b1 = b0[b0>speed],b1[b1>speed]

    #find RMS and Relative RMS error
    urms = np.sqrt((a0.sub(a1)**2).sum()/len(a0))
    drms = np.sqrt((b0.sub(b1)**2).sum()/len(b0))

    x = (a0.sub(a1)/a1)**2
    y = (b0.sub(b1)/b1)**2
    a = a0.sub(a1)**2
    b = b0.sub(b1)**2
    rurms = np.sqrt((x).sum()/len(a0))
    rdrms = np.sqrt((y).sum()/len(b0))
    print 'Flood RMS = '+str(urms)
    print 'Ebb RMS = '+str(drms)
    print 'Flood Relative RMS = '+str(rurms)
    print 'Ebb Relative RMS = '+str(rdrms)
    print 'STD of error on flood = '+str(a.std())
    print 'STD of error on ebb = '+str(b.std())

    # Plot the adcp and fvcom timeseries.
    plt.figure()
    plt.rc('font',size='22')
    f0.plot(color='red',label='ADCP')
    f1.plot(color='blue',label='FVCOM')
    plt.grid(True)
    plt.legend(fontsize='18')
    plt.ylabel('Velocity (m/s)')
    plt.show()

    # Plot the squared difference between both datasets.
    f = f0.sub(f1)**2
    plt.figure()
    plt.rc('font',size='22')
    f.plot(color='black',label='ADCP - FVCOM')
    plt.grid(True)
    plt.legend(fontsize='18')
    plt.ylabel(r'Squared Difference $(m/s)^2$')
    #plt.show()

    # Plot Standard deviation
    plt.figure()
    plt.rc('font',size='22')
    s[0].plot(color='red',label='ADCP')
    s[1].plot(color='blue',label='FVCOM')
    plt.grid(True)
    plt.legend(fontsize='18')
    plt.ylabel(r'Standard Deviation $(m/s)$')
    #plt.show()
