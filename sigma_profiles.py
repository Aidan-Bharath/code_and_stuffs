from __future__ import division
from panelCut import *
import matplotlib as mpl

def magnitude(a):
    mag = np.sqrt(a['u']**2+a['v']**2+a['w']**2)
    return mag

def sigma_profile(p1,p2,adcp,gap,agap,timestart,timestop):
    """
    y = adcp.minor_axis[:]
    p3 = magnitude(p3)
    p1 = p1[::gap]
    p2 = p2[::gap]
    l = len(p1.iloc[:])
    a = len(p3.iloc[:])
    for i in xrange(l):
        print i
        plt.plot(p1.iloc[i],p2.iloc[i],color =(i/l,0.2,np.abs(i-l)/l,0.5))
    for i in xrange(a):
        print i
        plt.plot(p3.iloc[i],y,color = (0,0,0,1))
    plt.title('Sigma Layer Profiles')
    plt.show()
    """
    y = adcp.minor_axis[:]
    adcp = magnitude(adcp)
    p1 = p1[::gap]
    p2 = p2[::gap]
    adcp = adcp[::agap]
    l = len(p1.iloc[:])
    a = len(adcp.iloc[:])

    min, max = (0,l)
    step = 30

    # Setting up a colormap that's a simple transtion for probe
    mymap = mpl.colors.LinearSegmentedColormap.from_list('mycolors',['blue','red'])

    Z = [[0,0],[0,0]]
    levels = range(min,max+step,step)
    CS3 = plt.contourf(Z, levels, cmap=mymap)
    plt.clf()

    amin, amax = (0,a)
    astep = 1

    # Setting up a colormap that's a simple transtion for adcps
    mymapa = mpl.colors.LinearSegmentedColormap.from_list('mycolors',['blue','red'])

    Z = [[0,0],[0,0]]
    levels = range(amin,amax+astep,astep)
    CS2 = plt.contourf(Z, levels, cmap=mymapa)
    plt.clf()

    x = np.asarray(p1.iloc[:])
    z = np.asarray(p2.iloc[:])
    c = np.asarray(adcp.iloc[:])
    Z = np.linspace(0,l,l)
    A = np.linspace(0,a,a)

    r = (Z)/(max)
    g = 0
    b = 1-r
    ra = (A)/(amax)
    ga = 0
    ba = 1-ra

    fig,ax = plt.subplots()

    for i in xrange(len(Z)):
        ax.plot(x[i],z[i],color=(r[i],g,b[i],0.3))

    for i in xrange(len(A)):
        ax.plot(c[i],y,color = (ra[i],ga,ba[i],1),linewidth=4.0)

    plt.title('Decelerating Ebb Velocity Profiles between '+timestart+' and '+timestop)
    plt.xlabel('Velocity (m/s)')
    plt.ylabel('Depth (m)')
    cbar = plt.colorbar(CS2)
    cbar.ax.get_yaxis().set_ticks([])
    #for j, lab in enumerate(['$0$','$1$','$2$','$>3$']):
    #    cbar.ax.text(.5, (2 * j + 1) / 8.0, lab, ha='center', va='baseline')
    cbar.ax.get_yaxis().labelpad = 15
    cbar.ax.set_ylabel('Timestep Increase', rotation=270)
    plt.show()
    return p1


if __name__ == "__main__":

    adcp = '/home/aidan/thesis/probe_data/panels/2013/june_july/GP-130620-BPb_vel'
    el = '/home/aidan/thesis/probe_data/panels/2013/june_july/GP-130621-24-N2b_els'
    vel = '/home/aidan/thesis/probe_data/panels/2013/june_july/GP-130621-24-N2b_vels'

    adcp = pd.read_pickle(adcp)
    el = pd.read_pickle(el)
    vel = pd.read_pickle(vel)

    timestart = '2013-06-21 15:00:00'
    timestop = '2013-06-21 18:00:00'
    average = ['2013-06-21 15:40:00','2013-06-21 15:42:00']

    print adcp.major_xs(adcp.major_axis[1])['u']

    adcp = timeslice(adcp,timestart,timestop)
    el = timeslice(el,timestart,timestop)
    vel = timeslice(vel,timestart,timestop)

    s1,a1 = findtime(el,vel,average[0])
    s2,a2 = findtime(el,vel,average[1])
    a1,_ = findtime(adcp,adcp,average[0])
    a2,_ = findtime(adcp,adcp,average[1])

    gap = rolling_int(el,s1,s2)
    agap = rolling_int(adcp,a1,a2)

    sigma_profile(vel,el,adcp,gap,1,timestart,timestop)
