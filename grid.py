from __future__ import division
import netCDF4 as nc
import numpy as np
from datetime import datetime
from datetime import timedelta
import h5py


class grid:

    regioner = []
    ax = []
    time_cut = []
    time_range = []

    def __init__(self,filename,time=None,ax=None):
        self.data = nc.Dataset(filename).variables
        self.u = None
        self.v = None
        self.w = None
        self.ua = None
        self.va = None
        self.wa = None
        self.velocity = None
        self.da_velocity = None
        self.da_curl = None
        self.curl = None
        self.h = None
        self.eta = None
        self.lat = None
        self.lon = None
        self.latc = None
        self.lonc = None
        self.siglev = None
        self.region_e = None
        self.region_n = None

        grid.ax = ax or []
        if len(grid.ax) != 0:
            grid.regioner = True
        else:
            grid.regioner = False
        #grid.ax = np.array(grid.ax)

        time_check = time or []
        if len(time_check) != 0:
            grid.time_cut = True
            grid.time_range = np.array(time,dtype='datetime64[us]')
            td = self.data['time'][:]+678942
            self.time = np.array(td)
            t = len(self.time)
            l = []
            for i in xrange(t):
                date = datetime.fromordinal(int(self.time[i]))+timedelta(days=self.time[i]%1)-timedelta(days=366)
                l.append(date)
            self.time = np.array(l,dtype='datetime64[us]')
            self.argtime = np.argwhere((self.time>=grid.time_range[0])&(self.time<=grid.time_range[-1])).flatten()
            self.time = self.time[self.argtime]
        else:
            grid.time_cut = False

    def siglevel(self):
        run = []
        self.siglev = np.abs(self.data['siglev'][:,0])
        for i in range(self.siglev.shape[0]-1):
            run.append(self.siglev[i+1]-self.siglev[i])
        self.siglev = np.array(run)

    def el_region(self):
        self.latc = self.data['latc'][:]
        self.lonc = self.data['lonc'][:]
        self.lonc = np.intersect1d(np.argwhere(self.lonc<=grid.ax[0]),np.argwhere(self.lonc>=grid.ax[1]))
        self.latc = np.intersect1d(np.argwhere(self.latc>=grid.ax[2]),np.argwhere(self.latc<=grid.ax[3]))
        self.region_e = np.intersect1d(self.latc,self.lonc)
        self.latc = None
        self.lonc = None

    def n_region(self):
        self.lat = self.data['lat'][:]
        self.lon = self.data['lon'][:]
        self.lon = np.intersect1d(np.argwhere(self.lon<=grid.ax[0]),np.argwhere(self.lon>=grid.ax[1]))
        self.lat = np.intersect1d(np.argwhere(self.lat>=grid.ax[2]),np.argwhere(self.lat<=grid.ax[3]))
        self.region_n = np.intersect1d(self.lat,self.lon)
        self.lat = None
        self.lon = None

    def depth(self):
        if grid.regioner == True:
            self.n_region()
            self.h = self.data['h'][self.region_n]
        else:
            self.h = self.data['h'][:]

    def elevation(self):
        if grid.time_cut == True:
            if grid.regioner == True:
                self.n_region()
                self.eta = self.data['zeta'][self.argtime,self.region_n]
            else:
                self.eta = self.data['zeta'][self.argtime,:]
        else:
            if grid.regioner == True:
                self.n_region()
                self.eta = self.data['zeta'][:,self.region_n]
            else:
                self.eta = self.data['zeta'][:]

    def da_speed(self,vel=False,clear=False):

        if self.ua == None:
            #self.latc = np.zeros([])
            #self.lonc = np.zeros([])
            if grid.time_cut == True:
                self.siglevel()
                if grid.regioner == True:
                    self.el_region()
                    self.ua = self.data['ua'][self.argtime,self.region_e]
                    self.va = self.data['va'][self.argtime,self.region_e]
                    self.wa = np.sum(self.data['ww'][self.argtime,:,self.region_e]*self.siglev[None,:,None],axis=1)
                else:
                    self.ua = self.data['ua'][self.argtime,:]
                    self.va = self.data['va'][self.argtime,:]
                    self.wa = np.sum(self.data['ww'][self.argtime,:,:]*self.siglev[None,:,None],axis=1)
            else:
                if grid.regioner == True:
                    self.el_region()
                    self.ua = self.data['ua'][:,self.region_e]
                    self.va = self.data['va'][:,self.region_e]
                    self.wa = np.sum(self.data['ww'][:,:,self.region_e]*self.siglev[None,:,None],axis=1)
                else:
                    self.ua = self.data['ua'][:]
                    self.va = self.data['va'][:]
                    self.wa = np.sum(self.data['ww'][:]*self.siglev[None,:,None],axis=1)

        if vel == True:
            self.da_velocity = np.sqrt(self.ua**2+self.va**2+self.wa**2)

        if clear == True:
            self.ua = None
            self.va = None
            self.wa = None

    def speed(self,vel=False,clear=False):

        if self.u == None:
            if grid.time_cut == True:
                if grid.regioner == True:
                    self.el_region()
                    self.u = self.data['u'][self.argtime,:,self.region_e]
                    self.v = self.data['v'][self.argtime,:,self.region_e]
                    self.w = self.data['ww'][self.argtime,:,self.region_e]
                else:
                    self.u = self.data['u'][self.argtime,:]
                    self.v = self.data['v'][self.argtime,:]
                    self.w = self.data['ww'][self.argtime,:]
            else:
                if grid.regioner == True:
                    self.el_region()
                    self.u = self.data['u'][:,:,self.region_e]
                    self.v = self.data['v'][:,:,self.region_e]
                    self.w = self.data['ww'][:,:,self.region_e]
                else:
                    self.u = self.data['u'][:]
                    self.v = self.data['v'][:]
                    self.w = self.data['ww'][:]

        if vel == True:
            self.velocity = np.sqrt(self.u**2+self.v**2+self.w**2)

        if clear == True:
            self.u = None
            self.v = None
            self.w = None


    def vorticity(self,davg=True,clear=True):

        if grid.regioner == True:
            grid.regioner = False
            r_changed = True

        if davg == True:
            if r_changed == True:
                self.ua = None
                self.va = None
                self.wa = None

            self.da_speed()
            nbe = self.data['nbe'][:]
            a2u = self.data['a2u'][:]
            a1u = self.data['a1u'][:]

            self.da_curl = np.zeros([self.argtime.shape[0],self.ua.shape[1]])
            for j in range(self.argtime.shape[0]):
                dudy=a2u[0,:]*self.ua[j,:]+a2u[1,:]*self.ua[j,nbe[0,:]-1]+a2u[2,:]*self.ua[j,nbe[1,:]-1]+a2u[3,:]*self.ua[j,nbe[2,:]-1]
                dvdx=a1u[0,:]*self.va[j,:]+a1u[1,:]*self.va[j,nbe[0,:]-1]+a1u[2,:]*self.va[j,nbe[1,:]-1]+a1u[3,:]*self.va[j,nbe[2,:]-1]

                self.da_curl[j,:] = dvdx-dudy

            dvdx = None
            dudy = None
            nbe = None
            a2u = None
            a1u = None

            if clear == True:
                self.ua = None
                self.va = None
                self.wa = None

            if r_changed == True:
                grid.regioner = True
                self.el_region()
                self.da_curl = self.da_curl[:,self.region_e]
                r_changed = False

        else:
            if r_changed == True:
                self.u = None
                self.v = None
                self.w = None
            self.speed()
            self.siglevel()
            nbe = self.data['nbe'][:]
            a2u = self.data['a2u'][:]
            a1u = self.data['a1u'][:]

            self.curl = np.zeros([self.argtime.shape[0],self.siglev.shape[0],self.u.shape[2]])
            for j in range(self.argtime.shape[0]):
                for i in range(self.siglev.shape[0]):
                    dudy=a2u[0,:]*self.u[j,i,:]+a2u[1,:]*self.u[j,i,nbe[0,:]-1]+a2u[2,:]*self.u[j,i,nbe[1,:]-1]+a2u[3,:]*self.u[j,i,nbe[2,:]-1]
                    dvdx=a1u[0,:]*self.v[j,i,:]+a1u[1,:]*self.v[j,i,nbe[0,:]-1]+a1u[2,:]*self.v[j,i,nbe[1,:]-1]+a1u[3,:]*self.v[j,i,nbe[2,:]-1]

                    self.curl[j,i,:] = dvdx-dudy

            dvdx = None
            dudy = None
            nbe = None
            a2u = None
            a1u = None

            if clear == True:
                self.u = None
                self.v = None
                self.w = None

            if r_changed == True:
                grid.regioner = True
                self.el_region()
                self.curl = self.curl[:,:,self.region_e]
                r_changed = False

    def save(self,filename):
        self.region_e = None
        self.region_n = None
        mask = np.array(self.__dict__.items())
        print mask
        print mask.shape[0]
        dat = np.argwhere((mask=='data'))[0]
        print dat
        arg = np.argwhere((mask=='argtime'))[0]
        sig = np.argwhere((mask=='siglev'))[0]
        mask[dat] = None
        mask[sig] = None
        mask[arg] = None
        l = np.argwhere([mask[i,1]!=None for i in xrange(0,mask.shape[0])]).flatten()
        print mask
        mask = mask[l]
        print l
        print mask

        #savefile.create_dataset(self,self.__dict__)
        #savefile = h5py.File(filename, 'a')
        #savefile.create_dataset('time',self.time.shape,self.time,dtype='datetime64[us]')
        #del self.time

        #for i,j in self.__dict__.items():
        #    savefile.create_dataset(i,data=self.__dict__[i])#,dtype=self.__dict__[i].dtype)




    def __repr__(self):
        return ('ua = %s , va = %s , wa = %s \n'
                'u = %s , v = %s , w = %s \n'
                'davg_Velocity = %s , Layer Velocity = %s \n'
                'davg_Vorticity = %s , Layer Vorticity = %s \n'
                'h = %s , eta = %s \n'
                'Regioned = %s , Timesliced = %s'
                %(repr(self.ua.shape),repr(self.va.shape),repr(self.wa.shape),repr(self.u.shape),repr(self.v.shape),repr(self.w.shape),repr(self.da_velocity.shape),repr(self.velocity.shape),repr(self.da_curl.shape),repr(self.curl.shape),repr(self.h.shape),repr(self.eta.shape),repr(grid.regioner),repr(grid.time_cut)))

