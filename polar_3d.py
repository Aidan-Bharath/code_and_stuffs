from __future__ import division
from panelCut import *
from matplotlib import cm
from PySide.QtCore import *
from PySide.QtGui import *
import sys
import os

def magnitude(a):
    mag = np.sqrt(a['u']**2+a['v']**2+a['w']**2)
    return mag

def polar3d(probe,adcp,timestart,timestop):
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    #probe = probe.mean(axis=2)
    #probe = probe[::20]
    #adcp = adcp.mean(axis=2)
    #adcp = adcp[::20]

    theta_probe = np.arctan2(probe['v'],probe['u'])
    mag_probe = magnitude(probe)
    theta_adcp = np.arctan2(adcp['v'],adcp['u'])
    mag_adcp = magnitude(adcp)

    X = mag_probe*np.cos(theta_probe)
    Y = mag_probe*np.sin(theta_probe)
    A = mag_adcp*np.cos(theta_adcp)
    B = mag_adcp*np.sin(theta_adcp)

    Z = np.linspace(0,probe['u'].index[-1].hour - probe['u'].index[0].hour,len(X))
    print Z
    C = np.linspace(0,probe['u'].index[-1].hour - probe['u'].index[0].hour,len(A))

    ax.plot(X,Y,Z,color='blue',label='GP-BPb-FVCOM')
    ax.plot(A,B,C,color='red',label='GP-BPb-ADCP')
    ax.set_xlabel('Eastern Velocity (m/s)')
    ax.set_ylabel('Northern Velocity (m/s)')
    ax.set_zlabel('Time (hr)')
    ax.set_xlim((-0.25,0.65))
    ax.set_ylim((0.5,2))
    plt.legend()
    plt.title('Depth Averaged Velocity Magnitude between \n '+timestart+' and '+timestop)
    plt.show()

if __name__ == "__main__":

    """
    app = QApplication(sys.argv)
    caption = 'Open Files'
    directory = './'
    adcp = QFileDialog.getOpenFileNames(None, caption, directory)[0]
    adcp = adcp[0]
    p1 = QFileDialog.getOpenFileNames(None, caption, directory)[0]
    p1 = p1[0]
    """

    bpb = '/home/aidan/thesis/probe_data/panels/2013/june_july/GP-130621-24-BPb_sigmas'
    ta = '/home/aidan/thesis/probe_data/panels/2013/june_july/GP-130621-BPb-hr'

    bpb = pd.read_pickle(bpb)
    ta = pd.read_pickle(ta)

    bpb = bpb.mean(axis=2)
    ta = ta.mean(axis=2)
    bpb = bpb.reindex(index=bpb.index.to_datetime())
    ta = ta.reindex(index=ta.index.to_datetime())
    ta = ta.resample('2T')

    time = ['2013-06-21 08:00:00','2013-06-21 12:00:00']
    bpb = bpb[time[0]:time[1]]
    ta = ta[time[0]:time[1]]
    polar3d(bpb,ta,time[0],time[1])
