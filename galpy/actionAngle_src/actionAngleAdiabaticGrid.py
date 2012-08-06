###############################################################################
#   actionAngle: a Python module to calculate  actions, angles, and frequencies
#
#      class: actionAngleAdiabaticGrid
#
#             build grid in integrals of motion to quickly evaluate 
#             actionAngleAdiabatic
#
#      methods:
#             __call__: returns (jr,lz,jz)
#
###############################################################################
import math
import numpy
from scipy import interpolate
from actionAngleAdiabatic import actionAngleAdiabatic
from galpy.actionAngle import actionAngle, UnboundError
import galpy.potential
from matplotlib import pyplot
class actionAngleAdiabaticGrid():
    """Action-angle formalism for axisymmetric potentials using the adiabatic approximation, grid-based interpolation"""
    def __init__(self,pot=None,zmax=3./8.,gamma=1.,Rmax=3.,
                 nR=25,nEz=25,nEr=25,nLz=25,**kwargs):
        """
        NAME:
           __init__
        PURPOSE:
           initialize an actionAngleAdiabaticGrid object
        INPUT:
           pot= potential or list of potentials (planarPotentials)
           zmax= zmax for building Ez grid
           Rmax = Rmax for building grids
           gamma= (default=1.) replace Lz by Lz+gamma Jz in effective potential
           nEz=, nEr=, nLz, nR= grid size
           +scipy.integrate.quad keywords
        OUTPUT:
        HISTORY:
            2012-07-27 - Written - Bovy (IAS@MPIA)
        """
        if pot is None:
            raise IOError("Must specify pot= for actionAngleAxi")
        self._gamma= gamma
        self._pot= pot
        self._zmax= zmax
        self._Rmax= Rmax
        self._Rmin= 0.01
        #Set up the actionAngleAdiabatic object that we will use to interpolate
        self._aA= actionAngleAdiabatic(pot=self._pot,gamma=self._gamma)
        #Build grid for Ez, first calculate Ez(zmax;R) function
        self._Rs= numpy.linspace(self._Rmin,self._Rmax,nR)
        self._EzZmaxs= numpy.array([galpy.potential.evaluatePotentials(r,self._zmax,self._pot)-
                                    galpy.potential.evaluatePotentials(r,0.,self._pot) for r in self._Rs])
        self._EzZmaxsInterp= interpolate.InterpolatedUnivariateSpline(self._Rs,numpy.log(self._EzZmaxs),k=3)
        y= numpy.linspace(0.,1.,nEz)
        jz= numpy.zeros((nR,nEz))
        jzEzzmax= numpy.zeros(nR)
        for ii in range(nR):
            for jj in range(nEz):
                #Calculate Jz
                jz[ii,jj]= self._aA.Jz(self._Rs[ii],0.,1.,#these two r dummies
                                       0.,math.sqrt(2.*y[jj]*self._EzZmaxs[ii]),
                                       **kwargs)[0]
                if jj == nEz-1: 
                    jzEzzmax[ii]= jz[ii,jj]
        for ii in range(nR): jz[ii,:]/= jzEzzmax[ii]
        #First interpolate Ez=Ezmax
        self._jzEzmaxInterp= interpolate.InterpolatedUnivariateSpline(self._Rs,numpy.log(jzEzzmax+10.**-5.),k=3)
        self._jzInterp= interpolate.RectBivariateSpline(self._Rs,
                                                        y,
                                                        jz,
                                                        kx=3,ky=3,s=0.)
        #JR grid
        self._Lzmin= 0.01
        self._Lzs= numpy.linspace(self._Lzmin,
                                  self._Rmax\
                                      *galpy.potential.vcirc(self._pot,
                                                             self._Rmax),
                                  nLz)
        self._Lzmax= self._Lzs[-1]
        #Calculate ER(vr=0,R=RL)
        self._RL= numpy.array([galpy.potential.rl(self._pot,l) for l in self._Lzs])
        self._RLInterp= interpolate.InterpolatedUnivariateSpline(self._Lzs,
                                                                 self._RL,k=3)
        self._ERRL= numpy.array([galpy.potential.evaluatePotentials(self._RL[ii],0.,self._pot) +self._Lzs[ii]**2./2./self._RL[ii]**2. for ii in range(nLz)])
        self._ERRLmax= numpy.amax(self._ERRL)+1.
        self._ERRLInterp= interpolate.InterpolatedUnivariateSpline(self._Lzs,
                                                                   numpy.log(-(self._ERRL-self._ERRLmax)),k=3)
        self._Ramax= 99.
        self._ERRa= numpy.array([galpy.potential.evaluatePotentials(self._Ramax,0.,self._pot) +self._Lzs[ii]**2./2./self._Ramax**2. for ii in range(nLz)])
        self._ERRamax= numpy.amax(self._ERRa)+1.
        self._ERRaInterp= interpolate.InterpolatedUnivariateSpline(self._Lzs,
                                                                   numpy.log(-(self._ERRa-self._ERRamax)),k=3)
        y= numpy.linspace(0.,1.,nEr)
        jr= numpy.zeros((nLz,nEr))
        jrERRa= numpy.zeros(nLz)
        for ii in range(nLz):
            for jj in range(nEr-1): #Last one is zero by construction
                try:
                    jr[ii,jj]= self._aA.JR(self._RL[ii],
                                           numpy.sqrt(2.*(self._ERRa[ii]+y[jj]*(self._ERRL[ii]-self._ERRa[ii])-galpy.potential.evaluatePotentials(self._RL[ii],0.,self._pot))-self._Lzs[ii]**2./self._RL[ii]**2.),
                                           self._Lzs[ii]/self._RL[ii],
                                           0.,0.,
                                           **kwargs)[0]
                except UnboundError:
                    raise
                if jj == 0: 
                    jrERRa[ii]= jr[ii,jj]
        for ii in range(nLz): jr[ii,:]/= jrERRa[ii]
        #First interpolate Ez=Ezmax
        self._jr= jr
        self._jrERRaInterp= interpolate.InterpolatedUnivariateSpline(self._Lzs,
                                                                     numpy.log(jrERRa+10.**-5.),k=3)
        self._jrInterp= interpolate.RectBivariateSpline(self._Lzs,
                                                        y,
                                                        jr,
                                                        kx=3,ky=3,s=0.)
        return None

    def __call__(self,*args,**kwargs):
        """
        NAME:
           __call__
        PURPOSE:
           evaluate the actions (jr,lz,jz)
        INPUT:
           Either:
              a) R,vR,vT,z,vz
              b) Orbit instance: initial condition used if that's it, orbit(t)
                 if there is a time given as well
           scipy.integrate.quadrature keywords
        OUTPUT:
           (jr,lz,jz)
        HISTORY:
           2012-07-27 - Written - Bovy (IAS@MPIA)
        NOTE:
           For a Miyamoto-Nagai potential, this seems accurate to 0.1% and takes ~0.13 ms
           For a MWPotential, this takes ~ 0.17 ms
        """
        meta= actionAngle(*args)
        #First work on the vertical action
        Phi= galpy.potential.evaluatePotentials(meta._R,meta._z,self._pot)
        Phio= galpy.potential.evaluatePotentials(meta._R,0.,self._pot)
        Ez= Phi-Phio+meta._vz**2./2.
        #Bigger than Ezzmax?
        thisEzZmax= numpy.exp(self._EzZmaxsInterp(meta._R))
        if meta._R > self._Rmax or meta._R < self._Rmin or (Ez != 0 and numpy.log(Ez) > thisEzZmax): #Outside of the grid
            print "Outside of grid in Ez", meta._R > self._Rmax , meta._R < self._Rmin , (Ez != 0 and numpy.log(Ez) > thisEzZmax)
            jz= self._aA.Jz(meta._R,0.,1.,#these two r dummies
                            0.,math.sqrt(2.*Ez),
                            **kwargs)[0]
        else:
            jz= (self._jzInterp(meta._R,Ez/thisEzZmax)\
                *(numpy.exp(self._jzEzmaxInterp(meta._R))-10.**-5.))[0][0]
        #Radial action
        ERLz= math.fabs(meta._R*meta._vT)+self._gamma*jz
        ER= Phio+meta._vR**2./2.+ERLz**2./2./meta._R**2.
        thisRL= self._RLInterp(ERLz)
        thisERRL= -numpy.exp(self._ERRLInterp(ERLz))+self._ERRLmax
        thisERRa= -numpy.exp(self._ERRaInterp(ERLz))+self._ERRamax
        if (ER-thisERRa)/(thisERRL-thisERRa) > 1. \
                and ((ER-thisERRa)/(thisERRL-thisERRa)-1.) < 10.**-2.:
            ER= thisERRL
        elif (ER-thisERRa)/(thisERRL-thisERRa) < 0. \
                and (ER-thisERRa)/(thisERRL-thisERRa) > -10.**-2.:
            ER= thisERRa
        #Outside of grid?
        if ERLz < self._Lzmin or ERLz > self._Lzmax \
                or (ER-thisERRa)/(thisERRL-thisERRa) > 1. \
                or (ER-thisERRa)/(thisERRL-thisERRa) < 0.:
            print "Outside of grid in ER/Lz", ERLz < self._Lzmin , ERLz > self._Lzmax \
                , (ER-thisERRa)/(thisERRL-thisERRa) > 1. \
                , (ER-thisERRa)/(thisERRL-thisERRa) < 0., ER, thisERRL, thisERRa, (ER-thisERRa)/(thisERRL-thisERRa)
            jr= self._aA.JR(thisRL,
                            numpy.sqrt(2.*(ER-galpy.potential.evaluatePotentials(thisRL,0.,self._pot))-ERLz**2./thisRL**2.),
                            ERLz/thisRL,
                            0.,0.,
                            **kwargs)[0]
        else:
            jr= (self._jrInterp(ERLz,
                               (ER-thisERRa)/(thisERRL-thisERRa))\
                *(numpy.exp(self._jrERRaInterp(ERLz))-10.**-5.))[0][0]
        return (jr,meta._R*meta._vT,jz)

    def Jz(self,*args,**kwargs):
        """
        NAME:
           Jz
        PURPOSE:
           evaluate the action jz
        INPUT:
           Either:
              a) R,vR,vT,z,vz
              b) Orbit instance: initial condition used if that's it, orbit(t)
                 if there is a time given as well
           scipy.integrate.quadrature keywords
        OUTPUT:
           jz
        HISTORY:
           2012-07-30 - Written - Bovy (IAS@MPIA)
        """
        meta= actionAngle(*args)
        Phi= galpy.potential.evaluatePotentials(meta._R,meta._z,self._pot)
        Phio= galpy.potential.evaluatePotentials(meta._R,0.,self._pot)
        Ez= Phi-Phio+meta._vz**2./2.
        #Bigger than Ezzmax?
        thisEzZmax= numpy.exp(self._EzZmaxsInterp(meta._R))
        if meta._R > self._Rmax or meta._R < self._Rmin or (Ez != 0. and numpy.log(Ez) > thisEzZmax): #Outside of the grid
            print "Outside of grid in Ez"
            jz= self._aA.Jz(meta._R,0.,1.,#these two r dummies
                            0.,math.sqrt(2.*Ez),
                            **kwargs)[0]
        else:
            jz= (self._jzInterp(meta._R,Ez/thisEzZmax)\
                *(numpy.exp(self._jzEzmaxInterp(meta._R))-10.**-5.))[0][0]
        return jz
