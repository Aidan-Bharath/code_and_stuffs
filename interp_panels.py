from structFunc import *


def magnitude(a):
    mag = np.sqrt(a['u']**2+a['v']**2+a['w']**2)
    return mag


if __name__ == "__main__":

    #### load adcp ndata and make the time conversion

    stats = False
    matDir = '/home/aidan/thesis/matfiles/GP130730_avg15.mat'
    ##### 2013+ mat file loader
    #u,v,w,binss,time,pres,error = load_mat(matDir,stats=stats)
    ##### 2012 mat file loader
    u,v,w,binss,time,pres,error = matdata(matDir)
    #### for 2012 data
    time = np.transpose(time)

    #### convert numerical time to datetime object
    time = conv_time(time)
    print 'done conversion for adcps'

    al_speeds = np.array([u,v,w])
    #al_speeds = np.swapaxes(al_speeds,1,2)
    print al_speeds.shape
    print 'speeds'
    index = np.array(time[0,:])
    print 'time'
    columns = ['u','v','w']
    dp = pd.Panel(al_speeds,items=columns,major_axis=index,minor_axis=binss[:,0])
    #dp = pd.Panel(al_speeds,items=columns,major_axis=index,minor_axis=binss[0,:])
    print 'panel made'
    pd.Panel.to_pickle(dp,'/home/aidan/thesis/probe_data/panels/2013/august/GP-130730-TA_vel')
    print 'done'

    #### Load probe data from raw output files 3d
    '''
    location = 5
    probeDir = '/home/aidan/thesis/probe_data/2012/3d_probe_data/july27-30/'
    probes = loadProbe(probeDir)

    #### Calculate the elevations of each sigma layer

    siglay = np.array([0.98999,0.94999,0.86999,0.74999,0.58999,0.41000,0.25000,0.13000,0.05000,0.01000])
    el,el_tot= sigmas(probes,location,siglay)

    #### For 3d set variables and prep for interpolations

    uu = probes[str(location)+'u-01']
    vv = probes[str(location)+'v-01']
    ww = probes[str(location)+'w-01']

    times = probes['time']+678941.986112 #original value from mitchell 678942
    onetime = times.flatten()
    t = len(onetime)

    #### Use fortran for the interpolation

    #### for 2013+ data
    #interp_u = np.empty((t,binss.shape[1]))
    #interp_v = np.empty((t,binss.shape[1]))
    #interp_w = np.empty((t,binss.shape[1]))

    #### for 2012 data
    interp_u = np.empty((t,binss.shape[0]))
    interp_v = np.empty((t,binss.shape[0]))
    interp_w = np.empty((t,binss.shape[0]))

    print 'Begin Interpolation'
    #### For 2013+ data
    #for i in xrange(t):
    #    a = linear(el[i,:],uu[i,:],binss[0,:])
    #    b = linear(el[i,:],vv[i,:],binss[0,:])
    #    c = linear(el[i,:],ww[i,:],binss[0,:])
    #    interp_u[i, :] = a
    #    interp_v[i, :] = b
    #    interp_w[i, :] = c

    #### for 2012 data
    for i in xrange(t):
        a = linear(el[i,:],uu[i,:],binss[:,0])
        b = linear(el[i,:],vv[i,:],binss[:,0])
        c = linear(el[i,:],ww[i,:],binss[:,0])
        interp_u[i, :] = a
        interp_v[i, :] = b
        interp_w[i, :] = c

    #### Find the index on the bin level where the water level is.
    #### 2012 data
    b = binss.ravel()
    p = pres.ravel()
    #### 2013+ data
    #b = binss[0,:]
    #p = pres[:,0]

    close = find_closest(b,p)-1
    e = el_tot.ravel()
    closefv = find_closest(b,e)-1

    #### Replace nans above the water line.

    ##### uncomment for 2013+ data
    #u = np.transpose(u)
    #v = np.transpose(v)
    #w = np.transpose(w)
    #error = np.transpose(error)

    l = len(close)
    for i in xrange(l):
        u[i,close[i]:] = np.nan
        v[i,close[i]:] = np.nan
        w[i,close[i]:] = np.nan
        error[i,close[i]:] = np.nan
    for i in xrange(t):
        interp_u[i,closefv[i]:] = np.nan
        interp_v[i,closefv[i]:] = np.nan
        interp_w[i,closefv[i]:] = np.nan

    print 'End Interpolate and Replacement'

    #### Construct the ADCP speed panel
    desiredBin = 10.11

    al_speeds = np.array([u,v,w])
    index = np.array(time[0,:])
    columns = ['u','v','w']
    dp = pd.Panel(al_speeds,items=columns,major_axis=index,minor_axis=binss[:,0])
    #pd.Panel.to_pickle(dp,'/home/aidan/thesis/probe_data/panels/2013/june_july/GP-130620-BPb_stats')
    dp = dp.minor_xs(desiredBin)
    dp = magnitude(dp)

    print dp

    #### Organize and data panel for fvcom probe data

    all_speeds = np.array([interp_u,interp_v,interp_w])
    print all_speeds.shape
    items = ['u','v','w']
    bins = np.transpose(binss)

    #### Compare to the ADCP data for phase correction

    length = 30
    rms = np.empty((length,1))
    for i in range(length):
        print i
        times = probes['time']+(678942-0.0006944*i)
        times = np.array([times]).transpose()
        print times.shape
        times = conv_time(times)
        times = times.flatten()
        dfp = pd.Panel(all_speeds,items=items, major_axis=times,minor_axis=binss[:,0])
        dfp = dfp.minor_xs(desiredBin)
        dfp = magnitude(dfp)
        connect = time_match(dfp,dp)
        rms[i,:] =  np.sqrt(np.sum((connect[0]-connect[1])**2))

    #### Construct the Shifted FVCOM dataframe

    rmin = np.argmin(rms)

    print 'The time shift is '+str(rmin)+' minutes'

    times = probes['time']+(678942-0.0006944*rmin)
    times = np.array([times]).transpose()
    times = conv_time(times)
    times = times.flatten()
    #dfp = pd.Panel(all_speeds,items=items, major_axis=times,minor_axis=binss[0,:])
    #pd.Panel.to_pickle(dfp,'/home/aidan/thesis/probe_data/panels/2013/june_july/GP-130624-26_BPa_p-int')

    print 'Done.'
    '''
