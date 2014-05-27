from structFunc import loadProbe
from datetime import timedelta
from datetime import datetime
import numpy as np
import pandas as pd

if __name__ == "__main__":

    location = 6
    fric = 'f.015'
    probeDir = '/home/aidan/thesis/probe_data/2013/jun21-24/'+str(fric)+'/'
    probes = loadProbe(probeDir)

    #### Calculate the elevations of each sigma layer

    siglay = np.array([0.98999,0.94999,0.86999,0.74999,0.58999,0.41000,0.25000,0.13000,0.05000,0.01000])

    #### For 3d set variables and prep for interpolations

    items = ['u','v','w']
    uu = probes[str(location)+'u']
    vv = probes[str(location)+'v']
    ww = probes[str(location)+'w']
    all_speeds = np.array([uu,vv,ww])

    times = probes['time']+678942 #original value from mitchell 678942
    lt = len(times)
    time = []
    for i in xrange(lt):
        date = datetime.fromordinal(int(times[i]))+timedelta(days=times[i]%1)-timedelta(days=366)
        time.append(date)
    dfp = pd.Panel(all_speeds,items=items, major_axis=time,minor_axis=siglay)
    pd.Panel.to_pickle(dfp,'/home/aidan/thesis/probe_data/panels/2013/fri_frames/june-july/BPb-s-'+str(fric))

