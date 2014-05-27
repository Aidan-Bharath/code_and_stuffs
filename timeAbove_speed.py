from __future__ import division
from panelCut import *
import matplotlib as mpl


#### So far for ADCPs only
def magnitude(a):
    mag = np.sqrt(a['u']**2+a['v']**2+a['w']**2)
    return mag


def time_above(adcp,speed):
    depth = adcp.minor_axis[:]
    length = len(adcp.major_axis[:])
    adcp = magnitude(adcp)
    above = adcp[adcp>=speed]
    print above
    above = pd.notnull(above)
    above[above==True] = 1
    above[above==False] = 0
    above = above.sum(axis=0)
    time = above/length
    time[time==0.0] = np.nan
    plt.plot(time,depth,marker='o')
    plt.title(r'Ratio of Time Spent Above $'+str(speed)+'$ $ m/s$ over Data Collection Period')
    plt.xlabel(r'Time Spent above $'+str(speed)+'$ $ m/s $')
    plt.ylabel(r'Depth $ m $')
    plt.show()

if __name__ == "__main__":
    adcp = '/home/aidan/thesis/probe_data/panels/2013/august/GP-130730-TA-vel'

    adcp = pd.read_pickle(adcp)

    speed = 1.8
    time_above(adcp,speed)
