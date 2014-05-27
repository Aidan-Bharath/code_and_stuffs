from panelCut import *
from multiprocessing import Pool

def load_panel(a):
    a = pd.read_pickle(a)
    return a

def means(a):
    if magn == True:
        a = np.sqrt(a['u']**2+a['v']**2+a['w']**2)

    if dep_avg == True:
        a = a[time[0]:time[1]].mean(axis=1)
    else:
        a = a[time[0]:time[1]]

    a = a.reindex(index=a.index.to_datetime())

    if mean == True:
        a = a.resample(sample,how='mean')
        return a
    if std == True:
        a = a.resample(sample,how='std')
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

if __name__ == "__main__":

    global time,sample,mean,std,dep_avg
    dep_avg = True
    magn = False
    time = ['2012-08-01','2012-08-02']
    sample = '10T'

    a1 = '/home/aidan/thesis/probe_data/panels/2012/flw_stn3_adcp_error'
    a2 = '/home/aidan/thesis/probe_data/panels/2012/flw_stn4_adcp_error'
    a3 = '/home/aidan/thesis/probe_data/panels/2012/flw_stn5_adcp_error'
    a = [a1,a2,a3]
    a = Pool().map(load_panel,a)
    a = Pool().map(time_index,a)
    a = [a[0][time[0]:time[1]],a[1][time[0]:time[1]],a[2][time[0]:time[1]]]
    a = Pool().map(resamp_std,a)
    print a
    '''
    mean = False
    adcp_vel = Pool().map(means,a)
    mean = False
    std = True
    adcp_std = Pool().map(means,a)
    std = False
    '''

    ##### TimeSeries plot
    fig = plt.figure()
    plt.rc('font',size='18')
    a[0].mean(axis=1).plot(label='Standard Deviation: Flow Station 3')
    a[1].mean(axis=1).plot(label='Standard Deviation: Flow Station 4')
    a[2].mean(axis=1).plot(label='Standard Deviation: Flow Station 5')
    plt.ylabel(r'Standard Deviation (m/s)')
    plt.legend(fontsize='17')
    plt.show()
    '''
    ##### Depth profile
    fig = plt.figure()
    plt.rc('font',size='18')
    plt.plot(a[0].mean(axis=0),a[0].columns.values,label='Error Velocity: Flow Station 3')
    plt.plot(a[1].mean(axis=0),a[1].columns.values,label='Error Velocity: Flow Station 4')
    plt.plot(a[2].mean(axis=0),a[2].columns.values,label='Error Velocity: Flow Station 5')
    plt.ylabel('Depth (m)')
    plt.xlabel('Error Velocity (m/s)')
    plt.legend(fontsize='17')
    plt.grid()
    plt.show()
    '''
