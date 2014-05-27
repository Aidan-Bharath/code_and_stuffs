from structFunc import loadProbe
from interp import linear
from datetime import timedelta
from datetime import datetime
import h5py as hp
import scipy as sp
import numpy as np
import pandas as pd

def load_mat(matdir,stats=False):
    dic = {}
    if stats==False:
        dic.update(hp.File(matdir))
        data = dic['data']
        u = data['east_vel']
        v = data['north_vel']
        w = data['vert_vel']
        binss = data['bins']
        error = data['error_vel']
        time = dic['time']
        time = time['mtime']
        pres = dic['pres']
        pres = pres['surf']
        return u,v,w,binss,time,pres,error
    else:
        dic.update(hp.File(matdir))
        data = dic['data']
        ustd = data['east_vel_std']
        vstd = data['north_vel_std']
        wstd = data['vert_vel_std']
        binss = data['bins']
        error = data['error_vel']
        time = dic['time']
        time = time['mtime']
        pres = dic['pres']
        pres = pres['surf']
        return ustd,vstd,wstd,binss,time,pres,error

def find_closest(A, target):
    """Based on the elevation from either fvcom or adcp files we find the bin that is
    just below the water level."""
    #A must be sorted
    idx = A.searchsorted(target)
    idx = np.clip(idx, 1, len(A)-1)
    left = A[idx-1]
    right = A[idx]
    idx -= target - left < right - target
    return idx

def sigmas(dicto,local,siglay,a,dim=True):
    """find the mean height of an element in the grid based of the average height of
    the surrounding nodes. We have to watch the naming here, fvcom puts out tails
    on probe files eg. el1 or el1-01. the values here must reflect what they are
    named or it will crash."""
    if a == 0:
        pos1 = str(local)+'el1'
        pos2 = str(local)+'el2'
        pos3 = str(local)+'el3'
    else:
        pos1 = str(local)+'el1'
        pos2 = str(local)+'el2'
        pos3 = str(local)+'el3'
    me = np.array([dicto[pos1],dicto[pos2],dicto[pos3]])
    maxx = np.mean(me,axis=0)
    if dim == True:
        mean = np.outer(maxx,siglay)
        return mean,maxx
    else:
        return maxx

def matdata(matDir,update=True):
    """Load and extract out the necessary data from a .mat file and separate out the
    data"""
    adcp = {}
    adcp.update(sp.io.loadmat(matDir))
    d = adcp['data']
    t = adcp['time']
    p = adcp['pres']
    p =p[0,0]
    t = t[0,0]
    time = t['mtime']
    pres = p['surf']
    data = d[0,0]
    error = data['error_vel']
    u = data['east_vel']
    w = data['vert_vel']
    v = data['north_vel']
    binss = data['bins']

    return u,v,w,binss,time,pres,error

if __name__ == "__main__":

    stats = False
    matDir = '/home/aidan/thesis/matfiles/GP130730_avg15.mat'
#    u,v,w,binss,time,pres,error = load_mat(matDir,stats=stats)
    u,v,w,binss,time,pres,error = matdata(matDir)

    newdata = False

    location = 2
    loc = 6
    items = ['u','v','w']
    fric = ['run1']
    siglay = np.array([0.98999,0.94999,0.86999,0.74999,0.58999,0.41000,0.25000,0.13000,0.05000,0.01000])

    for i,j in enumerate(fric):
        print 'Start '+str(j)
        probeDir = '/home/aidan/thesis/probe_data/2013/aug03-06/'+str(j)+'/'
        probes = loadProbe(probeDir)

        if i == 2:
            el,el_tot= sigmas(probes,loc,siglay,i)
        else:
            el,el_tot= sigmas(probes,location,siglay,i)

        if i == 0:
            uu = probes[str(location)+'u']
            vv = probes[str(location)+'v']
            ww = probes[str(location)+'w']
        elif i == 2:
            uu = probes[str(loc)+'u']
            vv = probes[str(loc)+'v']
            ww = probes[str(loc)+'w']
        else:
            uu = probes[str(location)+'u']
            vv = probes[str(location)+'v']
            ww = probes[str(location)+'w']

        times = probes['time']+678942 #original value from mitchell 678942
        lt = len(times)
        time = []
        for k in xrange(lt):
            date = datetime.fromordinal(int(times[k]))+timedelta(days=times[k]%1)-timedelta(days=366)
            time.append(date)

        t = len(time)

        if newdata == True:

            interp_u = np.empty((t,binss.shape[1]))
            interp_v = np.empty((t,binss.shape[1]))
            interp_w = np.empty((t,binss.shape[1]))

            for i in xrange(t):
                interp_u[i, :] = linear(el[i,:],uu[i,:],binss[0,:])
                interp_v[i, :] = linear(el[i,:],vv[i,:],binss[0,:])
                interp_w[i, :] = linear(el[i,:],ww[i,:],binss[0,:])

            closefv = find_closest(binss[0,:],el_tot.ravel())-1

            for i in xrange(t):
                interp_u[i,closefv[i]:] = np.nan
                interp_v[i,closefv[i]:] = np.nan
                interp_w[i,closefv[i]:] = np.nan

            speed = np.array([interp_u,interp_v,interp_w])
            dfp = pd.Panel(speed,items=items, major_axis=time,minor_axis=binss[0,:])
            pd.Panel.to_pickle(dfp,'/home/aidan/thesis/probe_data/panels/2013/august/TA-130803-'+str(j)+'_int')

        else:

            interp_u = np.empty((t,binss.shape[0]))
            interp_v = np.empty((t,binss.shape[0]))
            interp_w = np.empty((t,binss.shape[0]))

            for i in xrange(t):
                a = linear(el[i,:],uu[i,:],binss[:,0])
                b = linear(el[i,:],vv[i,:],binss[:,0])
                c = linear(el[i,:],ww[i,:],binss[:,0])
                interp_u[i, :] = a
                interp_v[i, :] = b
                interp_w[i, :] = c

            b = binss.ravel()
            e = el_tot.ravel()
            closefv = find_closest(b,e)-1

            for i in xrange(t):
                interp_u[i,closefv[i]:] = np.nan
                interp_v[i,closefv[i]:] = np.nan
                interp_w[i,closefv[i]:] = np.nan

            speed = np.array([interp_u,interp_v,interp_w])
            dfp = pd.Panel(speed,items=items, major_axis=time,minor_axis=binss[:,0])
            pd.Panel.to_pickle(dfp,'/home/aidan/thesis/probe_data/panels/2013/august/TA-130803-'+str(j)+'_int')
