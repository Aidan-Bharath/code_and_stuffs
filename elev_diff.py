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

def submean(a):
    b = a.mean()
    a = a.sub(b)
    return a

def resamp(a):
    a = a.resample('1T')
    return a


if __name__=="__main__":

    '''
    This calculates the differences between elevations from Pandas Series data
    and plots the results.
    '''

    # Directory of the Elevation Series.
    f0 = '/home/aidan/thesis/probe_data/panels/2013/fri_frames/june-july/BPb_el_f.01'
    f1 = '/home/aidan/thesis/probe_data/panels/2013/fri_frames/june-july/BPb_el_f.0125'
    f2 = '/home/aidan/thesis/probe_data/panels/2013/fri_frames/june-july/BPb_el_f.015'
    f3 = '/home/aidan/thesis/probe_data/panels/2013/fri_frames/june-july/BPb_el_f.02'
    f4 = '/home/aidan/thesis/probe_data/panels/2013/fri_frames/june-july/BPb_el_f.025'
    f5 = '/home/aidan/thesis/probe_data/panels/2013/fri_frames/june-july/BPb_el_f.05'
    fa = '/home/aidan/thesis/probe_data/panels/2013/fri_frames/june-july/BPb_el_adcp'


    # Create a list of directories, needed for Pool().
    f = [f0,f1,f2,f3,f4,f5,fa]

    # Load Series
    f = Pool().map(load_panel,f)

    # Reindex the Series and convert date index to datetime objects. Not
    # necessary if the index is already a datetime object. This is slow.
    #f = Pool().map(time_index,f)

    # Subtract the mean elevations from each dataset.
    f = Pool().map(submean,f)

    # Resample the raw data to mean data over a set time interval.
    f = Pool().map(resamp,f)

    # Rename data columns so they can be distinguished when joined together.
    f0 = f[0].rename(columns={'FVCOM_el':'f0.01'})
    f1 = f[1].rename(columns={'FVCOM_el':'f0.0125'})
    f2 = f[2].rename(columns={'FVCOM_el':'f0.015'})
    f3 = f[3].rename(columns={'FVCOM_el':'f0.02'})
    f4 = f[4].rename(columns={'FVCOM_el':'f0.025'})
    f5 = f[5].rename(columns={'FVCOM_el':'f0.05'})
    f = [f0,f1,f2,f3,f4,f5,f[6]]
    print f[6]

    # Combine the Series into a Dataframe and then subtract the lowest friction
    # value elevations from the others. The joining may not be necessary here
    # and the subtract could be done directly from the previous step.
    joined = pd.concat(f,axis=1)
    j0 = np.abs(joined['f0.01'].sub(joined['f0.01']))
    j1 = np.abs(joined['f0.0125'].sub(joined['f0.01']))
    j2 = np.abs(joined['f0.015'].sub(joined['f0.01']))
    j3 = np.abs(joined['f0.02'].sub(joined['f0.01']))
    j4 = np.abs(joined['f0.025'].sub(joined['f0.01']))
    j5 = np.abs(joined['f0.05'].sub(joined['f0.01']))
    j = [j0,j1,j2,j3,j4,j5]

    # Join the results from the subtraction into a dataframe. Joining the
    # results back up makes plotting easier.
    joined = pd.concat(j,axis=1)

    # Name the columns for plot legend.
    joined = joined.rename(columns={0:'f0.01',1:'f0.125',2:'f0.015',3:'f0.02',4:'f0.025',5:'f0.05'})

    # Resample data to ten minute averages for plotting.
    joined = joined.resample('10T')
    joined = joined[j0.index[0]:j0.index[-1]]

    # Plot the difference data.
    plt.figure()
    plt.rc('font',size='22')
    joined.plot()
    plt.ylabel('Elevation Difference (m)')
    plt.show()

