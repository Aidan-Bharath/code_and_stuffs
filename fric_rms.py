from __future__ import division
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

def load_panel(a):
    a = pd.read_pickle(a)
    return a

def time_index(a):
    a = a.reindex(index=a.index.to_datetime())
    return a

def theta(a):
    a = np.arctan2(a['v'],a['u'])
    return a

def resamp(a):
    a = a.resample('10T')
    return a

def magnitude(a):
    mag = np.sqrt(a['u']**2+a['v']**2+a['w']**2)
    return mag


if __name__=="__main__":

    f0 = '/home/aidan/thesis/probe_data/panels/2013/fri_frames/june-july/BPb-int-f.01'
    f1 = '/home/aidan/thesis/probe_data/panels/2013/fri_frames/june-july/BPb-int-f.0125'
    f2 = '/home/aidan/thesis/probe_data/panels/2013/fri_frames/june-july/BPb-int-f.015'
    f3 = '/home/aidan/thesis/probe_data/panels/2013/fri_frames/june-july/BPb-int-f.02'
    f4 = '/home/aidan/thesis/probe_data/panels/2013/fri_frames/june-july/BPb-int-f.025'
    f5 = '/home/aidan/thesis/probe_data/panels/2013/fri_frames/june-july/BPb-int-f.05'
    a = '/home/aidan/thesis/probe_data/panels/2013/june_july/GP-130620-BPb_vel'

    bf = [0.01,0.0125,0.015,0.020,0.025,0.05,'ADCP']
    f = [f0,f1,f2,f3,f4,f5,a]
    print 'loop 1'
    p = []
    for i,j in enumerate(f):
        p.append(pd.read_pickle(j))

    print 'loop 2'
    a = []
    for i,j in enumerate(p):
        a.append(np.arctan2(j['v'],j['u']))

    print 'loop 3'
    m = []
    for i,j in enumerate(p):
        m.append(magnitude(j))

    a_r = m[6].reindex(index=m[6].index.to_datetime())
    a_a = a[6].reindex(index=a[6].index.to_datetime())
    f = [m[0],m[1],m[2],m[3],m[4],m[5],a_r]
    a = [a[0],a[1],a[2],a[3],a[4],a[5],a_a]

    minspeed = 1.0
    print 'loop 4'
    m = []
    s = []
    for i,j in enumerate(f):
        m.append(j[j>minspeed].resample('10T'))
        s.append(j[j>minspeed].resample('10T',how='std'))

    g = []
    h = []
    for i in xrange(len(m)-1):
        g.append(m[i].shift(-20,freq='T'))
        h.append(s[i].shift(-20,freq='T'))

    m = [g[0],g[1],g[2],g[3],g[4],g[5],a_r]
    s = [h[0],h[1],h[2],h[3],h[4],h[5],a_a]

    print 'loop 5'
    u = []
    d = []
    for i,j in enumerate(a):
        x = j.resample('10T')
        u.append(x[x>0].dropna(axis=0,how='all'))
        d.append(x[x<0].dropna(axis=0,how='all'))

    print 'loop 6'
    tu = []
    td = []
    for i,j in enumerate(m):
        tu.append(j.loc[u[i].index])
        td.append(j.loc[d[i].index])

    print 'loop 7'
    rmsu = []
    rmsd = []
    for i,j in enumerate(tu):
        rmsu.append(np.abs(j-tu[-1])/j)
    for i,j in enumerate(td):
        rmsd.append(np.abs(j-td[-1])/j)

    print 'loop 8'
    mu = []
    md = []
    su = []
    sd = []
    for i,j in enumerate(rmsu):
        mu.append(j.mean())
        su.append(j.std())
    for i,j in enumerate(rmsd):
        md.append(j.mean())
        sd.append(j.std())


    plt.figure()
    plt.rc('font',size='22')
    for i in xrange(len(mu)):
        plt.plot(mu[i],mu[i].index.values,label='BF = '+str(bf[i]))
    plt.ylabel(r'Elevation $(m)$')
    plt.xlabel('Mean Relative Velocity Difference')
    plt.grid()
    plt.legend(fontsize='18')
    plt.show()


    plt.figure()
    plt.rc('font',size='22')
    for i in xrange(len(md)):
        plt.plot(md[i],md[i].index.values,label='BF = '+str(bf[i]))
    plt.ylabel(r'Elevation $(m)$')
    plt.xlabel('Mean Relative Velocity Difference')
    plt.grid()
    plt.legend(loc=2,fontsize='18')
    plt.show()
