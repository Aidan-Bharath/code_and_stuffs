from __future__ import division
import sys
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

def agreat(a):
    a = a[a>0]
    return a

def aless(a):
    a = a[a<0]
    return a

def mean(a):
    a = a.mean()
    return a
def std(a):
    a = a.std()
    return a

if __name__ == "__main__":

    '''
    This code analyzes the direction of the flow at various adcp bin
    elevations. The analysis is done separating ebb and flood tides based on
    direction of the flow. Mean directions in radians are printed in Latex
    format along with polar plots of the data.
    '''

    # Set directories for loading.
    f0 = '/home/aidan/thesis/probe_data/panels/2013/june_july/GP-130620-BPb_vel'
    f1 = '/home/aidan/thesis/probe_data/panels/2013/june_july/GP-130621-24_BPb_p-int'

    # Set the time interval of data to be analyzed.
    time0 = '2013-06-21 00:00:00'
    time1 = '2013-06-22 00:00:00'

    # Put directories into a list for Pool() and load.
    f = [f0,f1]
    f = Pool().map(load_panel,f)
    print f

    # Select the elevations that are to be analyzed.
    ## fs 5
    elt = f[0].minor_axis[30]
    elm = f[0].minor_axis[16]
    elb = f[0].minor_axis[4]
    ## fs 3 and 4
    #elt = 12.11
    #elm = 8.11
    #elb = 4.11

    # Slice the panels along the elevation axis for the elevations chosen
    # above. t = top, m = middle, b = bottom.
    f0t = f[0].minor_xs(elt)
    f0m = f[0].minor_xs(elm)
    f0b = f[0].minor_xs(elb)
    f1t = f[1].minor_xs(elt)
    f1m = f[1].minor_xs(elm)
    f1b = f[1].minor_xs(elb)

    # Lists of adcp, fvcom data elevation pairs.
    ft = [f0t,f1t]
    fm = [f0m,f1m]
    fb = [f0b,f1b]

    # Reindex the date index as datetime object. This cannot be done on a
    # Panel.
    ft = Pool().map(time_index,ft)
    fm = Pool().map(time_index,fm)
    fb = Pool().map(time_index,fb)

    # Resample the raw data to mean data for a certain time interval.
    ft = Pool().map(resamp,ft)
    fm = Pool().map(resamp,fm)
    fb = Pool().map(resamp,fb)

    # Slice the data to the time interval specified above. This is not done
    # with Pool() because the times cannot easily be passed to the function. It
    # can be done if time0 and time1 are made global variables.
    f0t = ft[0][time0:time1]
    f0m = fm[0][time0:time1]
    f0b = fb[0][time0:time1]
    f1t = ft[1][time0:time1]
    f1m = fm[1][time0:time1]
    f1b = fb[1][time0:time1]
    print f0t

    # Remake the elevation pairs.
    ft = [f0t,f1t]
    fm = [f0m,f1m]
    fb = [f0b,f1b]

    # Calculate the angle in radians from East based on u and v velocities. The
    # results carry a +/- sign base on north or south flow.
    at = Pool().map(theta,ft)
    am = Pool().map(theta,fm)
    ab = Pool().map(theta,fb)

    # Calculate the magnitude of the velocities.
    mt = Pool().map(magnitude,ft)
    mm = Pool().map(magnitude,fm)
    mb = Pool().map(magnitude,fb)

    # Plot the data in a polar plot.
    ax = plt.subplot(111,polar=True)
    plt.rc('font',size='22')
    ax.scatter(at[0], mt[0],s=40,color='red' ,marker='^',label = 'ADCP '+str(elt)+' m')
    ax.scatter(at[1], mt[1],s=40,color='blue' ,label = 'FVCOM '+str(elt)+' m')
    ax.scatter(am[0], mm[0],s=40,color='green' ,marker='^',label = 'ADCP '+str(elm)+' m')
    ax.scatter(am[1], mm[1],s=40,color='purple' ,label = 'FVCOM '+str(elm)+' m')
    ax.scatter(ab[0], mb[0],s=40,color='orange' ,marker='^',label = 'ADCP '+str(elb)+' m')
    ax.scatter(ab[1], mb[1],s=40,color='brown' ,label = 'FVCOM '+str(elb)+' m')
    ax.set_xticklabels(['E', 'NE','N','NW','W', 'SW', 'S', 'SE'])
    plt.legend(loc=2,fontsize='18')
    #plt.show()

    # Here the angle Series are separated based on flow direction.
    satg = Pool().map(agreat,at)
    satl = Pool().map(aless,at)
    samg = Pool().map(agreat,am)
    saml = Pool().map(aless,am)
    sabg = Pool().map(agreat,ab)
    sabl = Pool().map(aless,ab)

    # Calculate the mean angle over the separated datasets.
    atg = Pool().map(mean,satg)
    atl = Pool().map(mean,satl)
    amg = Pool().map(mean,samg)
    aml = Pool().map(mean,saml)
    abg = Pool().map(mean,sabg)
    abl = Pool().map(mean,sabl)

    aatg = Pool().map(std,satg)
    aatl = Pool().map(std,satl)
    aamg = Pool().map(std,samg)
    aaml = Pool().map(std,saml)
    aabg = Pool().map(std,sabg)
    aabl = Pool().map(std,sabl)

    # Calculated the directional gradient from the top elevation to the bottom.
    fgrada = (atg[0]-abg[0])/(elt-elb)
    fgradf = (atg[1]-abg[1])/(elt-elb)
    egrada = (atl[0]-abl[0])/(elt-elb)
    egradf = (atl[1]-abl[1])/(elt-elb)

    # Put the calculated values into a dataframe so that it can be printed in
    # latex.
    index = ['Flood '+str(elt)+' m (rad)','Flood '+str(elm)+' m (rad)','Flood '+str(elb)+' m (rad)','Ebb '+str(elt)+' m (rad)','Ebb '+str(elm)+' m (rad)','Ebb '+str(elb)+' m (rad)','Flood Gradient (rad/m)','Ebb Gradient (rad/m)']
    g = pd.Series([atg[1],amg[1],abg[1],atl[1],aml[1],abl[1],fgradf,egradf],index=index)
    h = pd.Series([atg[0],amg[0],abg[0],atl[0],aml[0],abl[0],fgrada,egrada],index=index)
    i = pd.Series([aatg[1],aamg[1],aabg[1],aatl[1],aaml[1],aabl[1],'--','--'],index=index)
    j = pd.Series([aatg[0],aamg[0],aabg[0],aatl[0],aaml[0],aabl[0],'--','--'],index=index)
    d = {'ADCP Mean':h,'ADCP STD':i,'FVCOM Mean':g,'FVCOM STD':j}
    df = pd.DataFrame(d)
    print df.to_latex()


    '''
    f&e RMS
    '''

    # Separate the velocity data into ebb and flood tide data based on the ebb
    # and flood directional data index.

    # Flood Tide.
    mtfa = mt[0][satg[0].index].abs()
    mtff = mt[1][satg[1].index].abs()
    mmfa = mm[0][samg[0].index].abs()
    mmff = mm[1][samg[1].index].abs()
    mbfa = mb[0][sabg[0].index].abs()
    mbff = mb[1][sabg[1].index].abs()

    # Ebb Tide
    mtea = mt[0][satl[0].index].abs()
    mtef = mt[1][satl[1].index].abs()
    mmea = mm[0][saml[0].index].abs()
    mmef = mm[1][saml[1].index].abs()
    mbea = mb[0][sabl[0].index].abs()
    mbef = mb[1][sabl[1].index].abs()

    # Calculate the RMS error between datasets.
    rtf = np.sqrt((mtff.sub(mtfa)**2).sum()/len(mtfa))
    rmf = np.sqrt((mmff.sub(mmfa)**2).sum()/len(mmfa))
    rbf = np.sqrt((mbff.sub(mbfa)**2).sum()/len(mbfa))
    rte = np.sqrt((mtef.sub(mtea)**2).sum()/len(mtea))
    rme = np.sqrt((mmef.sub(mmea)**2).sum()/len(mmea))
    rbe = np.sqrt((mbef.sub(mbea)**2).sum()/len(mbea))

    # Calculate the relative RMS error between datasets.
    rrtf = np.sqrt(((mtff.sub(mtfa)/mtff)**2).mean())
    rrmf = np.sqrt(((mmff.sub(mmfa)/mmff)**2).mean())
    rrbf = np.sqrt(((mbff.sub(mbfa)/mbff)**2).mean())
    rrte = np.sqrt(((mtef.sub(mtea)/mtef)**2).mean())
    rrme = np.sqrt(((mmef.sub(mmea)/mmef)**2).mean())
    rrbe = np.sqrt(((mbef.sub(mbea)/mbef)**2).mean())

    # Put the RMS error data into a dataframe so that it can be printed in
    # latex.
    index = ['Flood '+str(elt)+' m','Flood '+str(elm)+' m','Flood '+str(elb)+' m','Ebb '+str(elt)+' m','Ebb '+str(elm)+' m','Ebb '+str(elb)+' m']
    g = pd.Series([rtf,rmf,rbf,rte,rme,rbe],index=index)
    h = pd.Series([rrtf,rrmf,rrbf,rrte,rrme,rrbe],index=index)
    d = {'RMS Error $(m/s)$':g,'Relative RMS Error $(m/s)$':h}
    df = pd.DataFrame(d)
    print df.to_latex()
