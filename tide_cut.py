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

def resamp_std(a):
    a = a.resample('10T',how='std')
    return a

def angle(a):
    a = np.arctan2(a['v'],a['u'])
    return a

def angle_plus(a):
    a = a[a>0]
    return a

def angle_minus(a):
    a = a[a<0]
    return a

def getvalues(a):
    a = a.max().describe()
    return a

if __name__ == "__main__":

    a1 = '/home/aidan/thesis/probe_data/panels/2012/flw_stn3_adcp_error'
    a2 = '/home/aidan/thesis/probe_data/panels/2012/flw_stn4_adcp_error'
    a3 = '/home/aidan/thesis/probe_data/panels/2012/flw_stn5_adcp_error'
    a4 = '/home/aidan/thesis/probe_data/panels/2012/flw_stn3_adcp_corrected'
    a5 = '/home/aidan/thesis/probe_data/panels/2012/flw_stn4_adcp_corrected'
    a6 = '/home/aidan/thesis/probe_data/panels/2012/flw_stn5_adcp_corrected'
    a = [a1,a2,a3,a4,a5,a6]
    a = Pool().map(load_panel,a)
    a = [a[0],a[1],a[2],a[3].mean(axis=2),a[4].mean(axis=2),a[5].mean(axis=2)]
    a = Pool().map(time_index,a)
    b = Pool().map(angle,a[3:6])
    b_up = Pool().map(angle_plus,b)
    b_down = Pool().map(angle_minus,b)
    a_up1 = a[0].join(b_up[0],how='inner').drop('v',1)
    a_up2 = a[1].join(b_up[1],how='inner').drop('v',1)
    a_up3 = a[2].join(b_up[2],how='inner').drop('v',1)
    a_up = [a_up1,a_up2,a_up3]
    a_down1 = a[0].join(b_down[0],how='inner').drop('v',1)
    a_down2 = a[1].join(b_down[1],how='inner').drop('v',1)
    a_down3 = a[2].join(b_down[2],how='inner').drop('v',1)
    a_down = [a_down1,a_down2,a_down3]
    a_up = Pool().map(getvalues,a_up)
    a_down = Pool().map(getvalues,a_down)
    d = {'Flow Station 3':a_up[0],'Flow Station 4':a_up[1],'Flow Station 5':a_up[2]}
    frame = pd.DataFrame(d)
    x = frame.to_latex()
    print x
    d = {'Flow Station 3':a_down[0],'Flow Station 4':a_down[1],'Flow Station 5':a_down[2]}
    frame = pd.DataFrame(d)
    x = frame.to_latex()
    print x
