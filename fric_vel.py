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

def theta(a):
    a = np.arctan2(a['v'],a['u'])
    return a

def greater(a):
    a = a[a>0].dropna(axis=0,how='all')
    return a
def less(a):
    a = a[a<0].dropna(axis=0,how='all')
    return a
def above(a):
    a = a[a>1.0]
    return a


if __name__=="__main__":

    """
    This gives a comparison of the Depth profiles from various bottom friction
    values. This is set to compare everything to f.012 and plots the
    differences in mean profiles and the velocity difference with bottom
    friction.
    """

    # Specify the FVCOM sigma layer panels to compare.
    f0 = '/home/aidan/thesis/probe_data/panels/2013/fri_frames/june-july/BPb-s-f.01'
    f1 = '/home/aidan/thesis/probe_data/panels/2013/fri_frames/june-july/BPb-s-f.0125'
    f2 = '/home/aidan/thesis/probe_data/panels/2013/fri_frames/june-july/BPb-s-f.015'
    f3 = '/home/aidan/thesis/probe_data/panels/2013/fri_frames/june-july/BPb-s-f.02'
    f4 = '/home/aidan/thesis/probe_data/panels/2013/fri_frames/june-july/BPb-s-f.025'
    f5 = '/home/aidan/thesis/probe_data/panels/2013/fri_frames/june-july/BPb-s-f.05'
    a = '/home/aidan/thesis/probe_data/panels/2013/june_july/GP-130620-BPb_vel'

    # load ADCP data
    a = load_panel(a)
    at = theta(a)
    at = time_index(at)
    at = resamp(at)
    atg = greater(at)
    atl = less(at)
    a = magnitude(a)
    a = time_index(a)
    a = resamp(a)
    a = above(a)

    # Specify the percentage elevation of each sigma layer center for the used
    # configuration.
    siglay = np.array([0.98999,0.94999,0.86999,0.74999,0.58999,0.41000,0.25000,0.13000,0.05000,0.01000])
    bf = [0.01,0.0125,0.015,0.020,0.025,0.05]
    bfd = [0.0125,0.015,0.020,0.025,0.05]

    # Put together a list for Pool()
    f = [f0,f1,f2,f3,f4,f5]

    # Load the fvcom data.
    f = Pool().map(load_panel,f)

    # Calculate the signed angles
    t = Pool().map(theta,f)
    t = Pool().map(resamp,t)
    tg = Pool().map(greater,t)
    tl = Pool().map(less,t)

    # Calculate the Magnitude from the fvcom data.
    f = Pool().map(magnitude,f)

    # Reindex the date index to a datetime object. This is slow.
    #f = Pool().map(time_index,f)

    # Resample the raw data to mean data.
    f = Pool().map(resamp,f)

    # Cut speeds only above 1.0 m/s
    f1 = f
    f = Pool().map(above,f)

    # Find the differences between velocities at each sigma layer in the
    # datasets.
    t = []
    for i in xrange(len(f)-1):
        #t.append(np.abs(f[0].sub(f[i+1])))
        t.append(f1[0].sub(f1[i+1]))

    # Plot the mean profile differences. Here we should be careful, no where
    # has the difference between ebb and flood tide been taken into account.
    # That should be added to the code.
    plt.figure()
    plt.rc('font',size='22')
    for i in xrange(len(t)):
        plt.plot(t[i].mean(),siglay,label='BF = '+str(bfd[i]))
    plt.ylabel('Sigma Layer')
    plt.xlabel('Velocity Difference (m/s)')
    plt.grid()
    plt.legend(fontsize='18')
    plt.show()


    # Plot mean velocity profiles flood tide
    fig,ax = plt.subplots()
    plt.rc('font',size='22')
    for i in xrange(len(f)):
        ax.plot(f[i].loc[tg[i].index].mean(),siglay,label='BF = '+str(bf[i]))
    ax.set_ylabel('Sigma Layer')
    ax.legend(loc=2,fontsize='18')
    ax1 = ax.twinx()
    ax1.plot(a.loc[atg.index].mean(),a.mean().index,label='ADCP',color='black')
    ax1.set_ylim([0,20])
    ax1.set_ylabel(r'ADCP Elevation $(m)$')
    ax1.legend(loc=3,fontsize='18')
    plt.xlabel('Velocity (m/s)')
    plt.grid()
    plt.show()

    # Plot mean velocity profiles ebb tide
    fig,ax = plt.subplots()
    plt.rc('font',size='22')
    for i in xrange(len(f)):
        ax.plot(f[i].loc[tl[i].index].mean(),siglay,label='BF = '+str(bf[i]))
    ax.set_ylabel('Sigma Layer')
    ax.legend(loc=2,fontsize='18')
    ax1 = ax.twinx()
    ax1.plot(a.loc[atl.index].mean(),a.mean().index,label='ADCP',color='black')
    ax1.set_ylim([0,20])
    ax1.set_ylabel(r'ADCP Elevation $(m)$')
    ax1.legend(loc=3,fontsize='18')
    plt.xlabel('Velocity (m/s)')
    plt.grid()
    plt.show()

    # Plot the velocity difference versus bottom friction.
    x = []
    y = []
    plt.figure()
    plt.rc('font',size='22')
    for i in xrange(len(siglay)):
        el1 = []
        for j in xrange(len(t)):
            el1.append(t[j].iloc[:,i].mean())
        x.append(9-i)
        y.append((el1[-1]-el1[0])/(bfd[-1]-bfd[0]))
        plt.plot(bfd,el1,label='Layer '+str(9-i))
    plt.ylabel('Velocity Difference (m/s)')
    plt.xlabel('Bottom Friction')
    plt.grid()
    plt.legend(loc=2,fontsize='18')
    plt.show()

    # Based on a linear change in velocity with bottom friction print the slope
    # values in latex format.
    df = pd.DataFrame({'Slopes':pd.Series(y,index=x)})
    print df.to_latex()

