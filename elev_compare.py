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

def submean(a):
    b = a.mean()
    a = a.sub(b)
    return a

def high(a):
    a = a[a>0]
    return a

def low(a):
    a = a[a<0]
    return a

def std(a):
    a = a.resample('10T',how='std')
    return a

def resamp(a):
    a = a.resample('5T')
    return a


if __name__=="__main__":

    """
    This code compares the elevations between adcp and fvcom. It looks at the
    differences between both datasets and calculates statistics for them.
    """

    # Load elevation Series using Pool().
    f0 = '/home/aidan/thesis/probe_data/panels/2012/flw_stn3_adcp_elev'
    f1 = '/home/aidan/thesis/probe_data/panels/2012/flw_stn3_probe_elev'
    f2 = '/home/aidan/thesis/probe_data/panels/2012/flw_stn4_adcp_elev'
    f3 = '/home/aidan/thesis/probe_data/panels/2012/flw_stn4_probe_elev'
    f4 = '/home/aidan/thesis/probe_data/panels/2012/flw_stn5_adcp_elev'
    f5 = '/home/aidan/thesis/probe_data/panels/2012/flw_stn5_probe_elev'
    f = [f0,f1,f2,f3,f4,f5]
    f = Pool().map(load_panel,f)

    # Reindex date index to Datetime objects.
    f = Pool().map(time_index,f)

    # Resample raw data to mean data over a certain time interval.
    #f = Pool().map(resamp,f)

    # Specify a time interval and slice the data.
    time = ['2012-07-27','2012-07-29 20']
    f0 = f[0][time[0]:time[1]]
    f1 = f[1][time[0]:time[1]]
    f2 = f[2][time[0]:time[1]]
    f3 = f[3][time[0]:time[1]]
    f4 = f[4][time[0]:time[1]]
    f5 = f[5][time[0]:time[1]]

    # Rename the data so that it can be distinguished when joined together into
    # a Dataframe.
    f = [f0,f1,f2,f3,f4,f5]
    f0 = f[0].rename(columns={'elv':'FS3-ADCP_el'})
    f1 = f[1].rename(columns={'elv':'FS3-FVCOM_el'})
    f2 = f[2].rename(columns={'elv':'FS4-ADCP_el'})
    f3 = f[3].rename(columns={'elv':'FS4-FVCOM_el'})
    f4 = f[4].rename(columns={'elv':'FS5-ADCP_el'})
    f5 = f[5].rename(columns={'elv':'FS5-FVCOM_el'})
    f = [f0,f1,f2,f3,f4,f5]

    # Subtract the mean elevation from data.
    f = Pool().map(submean,f)

    # Calculate the Standard deviation of each dataset.
    s = Pool().map(std,f)

    # Take the difference between adcp and fvcom data.
    a = f[0]['FS3-ADCP_el'].sub(f[1]['FS3-FVCOM_el'])
    b = f[2]['FS4-ADCP_el'].sub(f[3]['FS4-FVCOM_el'])
    c = f[4]['FS5-ADCP_el'].sub(f[5]['FS5-FVCOM_el'])

    # Put the statistics from the differences in a dataframe and print it in
    # latex format.
    index = ['Maximum $(m)$','Minimum $(m)$','Standard Deviation $(m)$']
    a0 = pd.Series([a.max(),a.min(),a.std()],index=index)
    a1 = pd.Series([b.max(),b.min(),b.std()],index=index)
    a2 = pd.Series([c.max(),c.min(),c.std()],index=index)
    aS = {'FS3':a0,'FS4':a1,'FS5':a2}
    df = pd.DataFrame(aS)
    print df.to_latex()

    # Plot the Difference data.
    plt.figure()
    plt.rc('font',size='22')
    a.plot(label='FS3')
    b.plot(label='FS4')
    c.plot(label='FS5')
    plt.legend(fontsize='18')
    plt.grid(True)
    plt.ylabel('Elevation Difference (m)')
    #plt.show()

    # Plot adcp and fvcom elevations at individual sites.
    f1 = pd.concat([f[0],f[1]],axis=1)
    f2 = pd.concat([f[2],f[3]],axis=1)
    f3 = pd.concat([f[4],f[5]],axis=1)

    plt.rc('font',size='22')
    f1.plot(color = ['red','blue'],legend=False)
    plt.ylabel('Elevation Variation (m)')
    plt.legend(fontsize='18')
    #plt.show()

    plt.rc('font',size='22')
    f2.plot(color = ['red','blue'],legend=False)
    plt.ylabel('Elevation Variation (m)')
    plt.legend(fontsize='18')
    #plt.show()

    plt.rc('font',size='22')
    f3.plot(color = ['red','blue'],legend=False)
    plt.ylabel('Elevation Variation (m)')
    plt.legend(fontsize='18')
    #plt.show()
    plt.cla()

    # Split elevation data to above and below the mean.
    h = Pool().map(high,f)
    l = Pool().map(low,f)

    # Join fvcom and adcp pairs. Join 'inner' is used so that resample does not
    # need to be used.
    h0 = h[0].join(h[1],how='inner')
    h1 = h[2].join(h[3],how='inner')
    h2 = h[4].join(h[5],how='inner')
    l0 = l[0].join(l[1],how='inner')
    l1 = l[2].join(l[3],how='inner')
    l2 = l[4].join(l[5],how='inner')
    h = [h0,h1,h2]
    l = [l0,l1,l2]

    # Calculate the RMS errors on high and low tide.
    x1 = np.sqrt((h[0]['FS3-ADCP_el'].sub(h[0]['FS3-FVCOM_el'])**2).sum()/len(h[0]['FS3-FVCOM_el']))
    x2 = np.sqrt((h[1]['FS4-ADCP_el'].sub(h[1]['FS4-FVCOM_el'])**2).sum()/len(h[1]['FS4-FVCOM_el']))
    x3 = np.sqrt((h[2]['FS5-ADCP_el'].sub(h[2]['FS5-FVCOM_el'])**2).sum()/len(h[2]['FS5-FVCOM_el']))
    y1 = np.sqrt((l[0]['FS3-ADCP_el'].sub(l[0]['FS3-FVCOM_el'])**2).sum()/len(l[0]['FS3-FVCOM_el']))
    y2 = np.sqrt((l[1]['FS4-ADCP_el'].sub(l[1]['FS4-FVCOM_el'])**2).sum()/len(l[1]['FS4-FVCOM_el']))
    y3 = np.sqrt((l[2]['FS5-ADCP_el'].sub(l[2]['FS5-FVCOM_el'])**2).sum()/len(l[2]['FS5-FVCOM_el']))

    # Put the data in a Dataframe and plot it in Latex format.
    index = ['Maximum Flood ADCP $(m)$','Maximum Flood FVCOM $(m)$','RMS Error Flood $(m)$','Minimum Ebb ADCP $(m)$','Minimum Ebb FVCOM $(m)$','RMS Error Ebb $(m)$']
    a0 = pd.Series([h0.max()[0],h0.max()[1],x1,l0.min()[0],l0.min()[1],y1],index=index)
    a1 = pd.Series([h1.max()[0],h1.max()[1],x2,l1.min()[0],l1.min()[1],y2],index=index)
    a2 = pd.Series([h2.max()[0],h2.max()[1],x3,l2.min()[0],l2.min()[1],y3],index=index)
    aS = {'FS3':a0,'FS4':a1,'FS5':a2}
    df = pd.DataFrame(aS)
    print df.to_latex()

    # Relative difference.

    print x1/(h[0]['FS3-FVCOM_el'].mean())
    print y1/(l[0]['FS3-FVCOM_el'].mean())
    print x2/(h[1]['FS4-FVCOM_el'].mean())
    print y2/(l[1]['FS4-FVCOM_el'].mean())
    print x3/(h[2]['FS5-FVCOM_el'].mean())
    print y3/(l[2]['FS5-FVCOM_el'].mean())
