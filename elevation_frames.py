from structFunc import *
import matplotlib.dates as dt

def elv_plot(df1,df2,df3,df4):
    fig,ax = plt.subplots()
    ax.plot_date(df1.index.to_datetime(),df1['el'],'-',label ='adcp')
    ax.plot_date(df2.index.to_datetime(),df2['el'],'-',label ='probe1')
    ax.plot_date(df3.index.to_datetime(),df3['el'],'-',label ='probe2')
    ax.plot_date(df4.index.to_datetime(),df4['el'],'-',label ='probe3')
    ax.xaxis.set_minor_locator(dt.HourLocator(byhour=range(24), interval=6))
    ax.xaxis.set_minor_formatter(dt.DateFormatter('%H:%M\n%a,%d'))
    ax.xaxis.grid(True, which="minor")
    ax.yaxis.grid()
    ax.xaxis.set_major_locator(dt.MonthLocator())
    ax.xaxis.set_major_formatter(dt.DateFormatter('\n\n\n%b\n%Y'))
    plt.legend()
    plt.tight_layout()
    plt.ylabel('Elevation Variation (m)')
    plt.title('Elevation Comparison between 3 surrounding nodes in FVCOM to ADCPs Location')
    plt.show()

def sigmas(dicto,local,siglay,dim=True):
    """find the mean height of an element in the grid based of the average height of
    the surrounding nodes. We have to watch the naming here, fvcom puts out tails
    on probe files eg. el1 or el1-01. the values here must reflect what they are
    named or it will crash."""
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


if __name__ == "__main__":

    location = 6
    fric = 'f.015'
    probeDir = '/home/aidan/thesis/probe_data/2013/jun21-24/'+str(fric)+'/'
    probes = loadProbe(probeDir)
    siglay = np.array([0.98999,0.94999,0.86999,0.74999,0.58999,0.41000,0.25000,0.13000,0.05000,0.01000])
    el,el_tot= sigmas(probes,location,siglay)
    times = probes['time']+678942 #original value from mitchell 678942
    lt = len(times)
    time = []
    for k in xrange(lt):
        date = datetime.fromordinal(int(times[k]))+timedelta(days=times[k]%1)-timedelta(days=366)
        time.append(date)

    matDir = '/home/aidan/thesis/matfiles/2013/Flow_BPb_avg_5min.mat'
    u,v,w,binss,times,pres,error = load_mat(matDir)
    lt = len(times)
    timea = []
    print times[0,:][0]
    for k in xrange(lt):
        date = datetime.fromordinal(int(times[k,:][0]))+timedelta(days=times[k,:][0]%1)-timedelta(days=366)
        timea.append(date)


    adcp = pd.DataFrame({'ADCP_el':pres[0,:]},index=timea)
    fvcom = pd.DataFrame({'FVCOM_el':el_tot[:,0]},index=time)

    pd.DataFrame.to_pickle(adcp,'/home/aidan/thesis/probe_data/panels/2013/fri_frames/june-july/BPb_el_adcp')
    pd.DataFrame.to_pickle(fvcom,'/home/aidan/thesis/probe_data/panels/2013/fri_frames/june-july/BPb_el_'+str(fric))

