###############################################################################
#   actionAngle: a Python module to calculate  actions, angles, and frequencies
#
#      class: actionAngleSpherical
#
#      methods:
#             __call__: returns (jr,lz,jz)
#             actionsFreqs: returns (jr,lz,jz,Or,Op,Oz)
#             actionsFreqsAngles: returns (jr,lz,jz,Or,Op,Oz,ar,ap,az)
#
###############################################################################
import copy
import math as m
import numpy as nu
from scipy import integrate
from actionAngle import *
from actionAngleAxi import actionAngleAxi, potentialAxi
class actionAngleSpherical(actionAngle):
    """Action-angle formalism for spherical potentials"""
    def __init__(self,*args,**kwargs):
        """
        NAME:
           __init__
        PURPOSE:
           initialize an actionAngleSpherical object
        INPUT:
           pot= a Spherical potential
        OUTPUT:
        HISTORY:
           2013-12-28 - Written - Bovy (IAS)
        """
        if not kwargs.has_key('pot'):
            raise IOError("Must specify pot= for actionAngleSpherical")
        self._pot= kwargs['pot']
        #Also store a 'planar' (2D) version of the potential
        if isinstance(self._pot,list):
            self._2dpot= [p.toPlanar() for p in self._pot]
        else:
            self._2dpot= self._pot.toPlanar()
        #The following for if we ever implement this code in C
        self._c= False
        ext_loaded= False
        if ext_loaded and ((kwargs.has_key('c') and kwargs['c'])
                           or not kwargs.has_key('c')):
            self._c= True
        else:
            self._c= False
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
           fixed_quad= (False) if True, use n=10 fixed_quad integration
           scipy.integrate.quadrature keywords
        OUTPUT:
           (jr,lz,jz)
        HISTORY:
           2013-12-28 - Written - Bovy (IAS)
        """
        if kwargs.has_key('fixed_quad'):
            fixed_quad= kwargs['fixed_quad']
            kwargs.pop('fixed_quad')
        else:
            fixed_quad= False
        if len(args) == 5: #R,vR.vT, z, vz
            R,vR,vT, z, vz= args
        elif len(args) == 6: #R,vR.vT, z, vz, phi
            R,vR,vT, z, vz, phi= args
        else:
            meta= actionAngle(*args)
            R= meta._R
            vR= meta._vR
            vT= meta._vT
            z= meta._z
            vz= meta._vz
        if isinstance(R,float):
            R= nu.array([R])
            vR= nu.array([vR])
            vT= nu.array([vT])
            z= nu.array([z])
            vz= nu.array([vz])
        if self._c:
            pass
        else:
            Lz= R*vT
            Lx= -z*vT
            Ly= z*vR-R*vz
            L2= Lx*Lx+Ly*Ly+Lz*Lz
            E= self._pot(R,z)+vR**2./2.+vT**2./2.+vz**2./2.
            L= nu.sqrt(L2)
            #Actions
            Jphi= Lz
            Jz= L-nu.fabs(Lz)
            #Jr requires some more work
            #Set up an actionAngleAxi object for EL and rap/rperi calculations
            axiR= nu.sqrt(R**2.+z**2.)
            axivT= L/axiR
            axivR= (R*vR+z*vz)/axiR
            Jr= []
            for ii in range(len(axiR)):
                axiaA= actionAngleAxi(axiR[ii],axivR[ii],axivT[ii],
                                      pot=self._2dpot)
                (rperi,rap)= axiaA.calcRapRperi()
                EL= axiaA.calcEL()
                E, L= EL
                Jr.append(self._calc_jr(rperi,rap,E,L,fixed_quad,**kwargs))
            return (nu.array(Jr),Jphi,Jz)

    def actionsFreqs(self,*args,**kwargs):
        """
        NAME:
           actionsFreqs
        PURPOSE:
           evaluate the actions and frequencies (jr,lz,jz,Omegar,Omegaphi,Omegaz)
        INPUT:
           Either:
              a) R,vR,vT,z,vz
              b) Orbit instance: initial condition used if that's it, orbit(t)
                 if there is a time given as well
           fixed_quad= (False) if True, use n=10 fixed_quad integration
           scipy.integrate.quadrature keywords
        OUTPUT:
            (jr,lz,jz,Omegar,Omegaphi,Omegaz)
        HISTORY:
           2013-12-28 - Written - Bovy (IAS)
        """
        if kwargs.has_key('fixed_quad'):
            fixed_quad= kwargs['fixed_quad']
            kwargs.pop('fixed_quad')
        else:
            fixed_quad= False
        if len(args) == 5: #R,vR.vT, z, vz
            R,vR,vT, z, vz= args
        elif len(args) == 6: #R,vR.vT, z, vz, phi
            R,vR,vT, z, vz, phi= args
        else:
            meta= actionAngle(*args)
            R= meta._R
            vR= meta._vR
            vT= meta._vT
            z= meta._z
            vz= meta._vz
        if isinstance(R,float):
            R= nu.array([R])
            vR= nu.array([vR])
            vT= nu.array([vT])
            z= nu.array([z])
            vz= nu.array([vz])
        if self._c:
            pass
        else:
            Lz= R*vT
            Lx= -z*vT
            Ly= z*vR-R*vz
            L2= Lx*Lx+Ly*Ly+Lz*Lz
            E= self._pot(R,z)+vR**2./2.+vT**2./2.+vz**2./2.
            L= nu.sqrt(L2)
            #Actions
            Jphi= Lz
            Jz= L-nu.fabs(Lz)
            #Jr requires some more work
            #Set up an actionAngleAxi object for EL and rap/rperi calculations
            axiR= nu.sqrt(R**2.+z**2.)
            axivT= L/axiR
            axivR= (R*vR+z*vz)/axiR
            Jr= []
            Or= []
            Op= []
            for ii in range(len(axiR)):
                axiaA= actionAngleAxi(axiR[ii],axivR[ii],axivT[ii],
                                      pot=self._2dpot)
                (rperi,rap)= axiaA.calcRapRperi()
                EL= axiaA.calcEL()
                E, L= EL
                Jr.append(self._calc_jr(rperi,rap,E,L,fixed_quad,**kwargs))
                #Radial period
                if Jr[-1] < 10.**-9.: #Circular orbit
                    Or.append(self._pot.epifreq(axiR))
                    Op.append(self._pot.omegac(axiR))
                    continue
                Rmean= m.exp((m.log(rperi)+m.log(rap))/2.)
                Or.append(self._calc_or(Rmean,rperi,rap,E,L,fixed_quad,**kwargs))
                Op.append(self._calc_op(Or[-1],Rmean,rperi,rap,E,L,fixed_quad,**kwargs))
            Op= nu.array(Op)
            Oz= copy.copy(Op)
            Op[vT < 0.]*= -1.
            return (nu.array(Jr),Jphi,Jz,nu.array(Or),Op,Oz)
    
    def actionsFreqsAngles(self,*args,**kwargs):
        """
        NAME:
           actionsFreqsAngles
        PURPOSE:
           evaluate the actions, frequencies, and angles
           (jr,lz,jz,Omegar,Omegaphi,Omegaz,ar,ap,az)
        INPUT:
           Either:
              a) R,vR,vT,z,vz
              b) Orbit instance: initial condition used if that's it, orbit(t)
                 if there is a time given as well
           fixed_quad= (False) if True, use n=10 fixed_quad integration
           scipy.integrate.quadrature keywords
        OUTPUT:
            (jr,lz,jz,Omegar,Omegaphi,Omegaz,ar,aphi,az)
        HISTORY:
           2013-12-29 - Written - Bovy (IAS)
        """
        if kwargs.has_key('fixed_quad'):
            fixed_quad= kwargs['fixed_quad']
            kwargs.pop('fixed_quad')
        else:
            fixed_quad= False
        if len(args) == 5: #R,vR.vT, z, vz
            raise IOError("You need to provide phi when calculating angles")
        elif len(args) == 6: #R,vR.vT, z, vz, phi
            R,vR,vT, z, vz, phi= args
        else:
            meta= actionAngle(*args)
            R= meta._R
            vR= meta._vR
            vT= meta._vT
            z= meta._z
            vz= meta._vz
        if isinstance(R,float):
            R= nu.array([R])
            vR= nu.array([vR])
            vT= nu.array([vT])
            z= nu.array([z])
            vz= nu.array([vz])
            phi= nu.array([phi])
        if self._c:
            pass
        else:
            Lz= R*vT
            Lx= -z*vT
            Ly= z*vR-R*vz
            L2= Lx*Lx+Ly*Ly+Lz*Lz
            E= self._pot(R,z)+vR**2./2.+vT**2./2.+vz**2./2.
            L= nu.sqrt(L2)
            #Actions
            Jphi= Lz
            Jz= L-nu.fabs(Lz)
            #Jr requires some more work
            #Set up an actionAngleAxi object for EL and rap/rperi calculations
            axiR= nu.sqrt(R**2.+z**2.)
            axivT= L/axiR #these are really spherical coords, called axi bc they go in actionAngleAxi
            axivR= (R*vR+z*vz)/axiR
            axivz= (z*vR-R*vz)/axiR
            Jr= []
            Or= []
            Op= []
            ar= []
            az= []
            #Calculate the longitude of the ascending node
            asc= self._calc_long_asc(z,R,axivz,phi,Lz,L)
            for ii in range(len(axiR)):
                axiaA= actionAngleAxi(axiR[ii],axivR[ii],axivT[ii],
                                      pot=self._2dpot)
                (rperi,rap)= axiaA.calcRapRperi()
                EL= axiaA.calcEL()
                E, L= EL
                Jr.append(self._calc_jr(rperi,rap,E,L,fixed_quad,**kwargs))
                #Radial period
                if Jr[-1] < 10.**-9.: #Circular orbit
                    Or.append(self._pot.epifreq(axiR))
                    Op.append(self._pot.omegac(axiR))
                    continue
                Rmean= m.exp((m.log(rperi)+m.log(rap))/2.)
                Or.append(self._calc_or(Rmean,rperi,rap,E,L,fixed_quad,**kwargs))
                Op.append(self._calc_op(Or[-1],Rmean,rperi,rap,E,L,fixed_quad,**kwargs))
                #Angles
                ar.append(self._calc_angler(Or[-1],axiR[ii],Rmean,rperi,rap,
                                            E,L,axivR[ii],fixed_quad,**kwargs))
                az.append(0.)
            Op= nu.array(Op)
            Oz= copy.copy(Op)
            Op[vT < 0.]*= -1.
            ap= copy.copy(asc)
            ar= nu.array(ar)
            az= nu.array(az)
            ap[vT < 0.]-= az[vT < 0.]
            ap[vT >= 0.]+= az[vT >= 0.]
            ar= ar % (2.*nu.pi)
            ap= ap % (2.*nu.pi)
            az= az % (2.*nu.pi)
            return (nu.array(Jr),Jphi,Jz,nu.array(Or),Op,Oz,
                    ar,ap,az)
    
    def _calc_jr(self,rperi,rap,E,L,fixed_quad,**kwargs):
        if fixed_quad:
            return integrate.fixed_quad(_JrSphericalIntegrand,
                                        rperi,rap,
                                        args=(E,L,self._2dpot),
                                        n=10,
                                        **kwargs)[0]/nu.pi
        else:
            return (nu.array(integrate.quad(_JrSphericalIntegrand,
                                            rperi,rap,
                                            args=(E,L,self._2dpot),
                                            **kwargs)))[0]/nu.pi
    def _calc_or(self,Rmean,rperi,rap,E,L,fixed_quad,**kwargs):
        Tr= 0.
        if Rmean > rperi and not fixed_quad:
            Tr+= nu.array(integrate.quadrature(_TrSphericalIntegrandSmall,
                                               0.,m.sqrt(Rmean-rperi),
                                               args=(E,L,self._2dpot,
                                                     rperi),
                                               **kwargs))[0]
        elif Rmean > rperi and fixed_quad:
            Tr+= integrate.fixed_quad(_TrSphericalIntegrandSmall,
                                      0.,m.sqrt(Rmean-rperi),
                                      args=(E,L,self._2dpot,
                                            rperi),
                                      n=10,**kwargs)[0]
        if Rmean < rap and not fixed_quad:
            Tr+= nu.array(integrate.quadrature(_TrSphericalIntegrandLarge,
                                               0.,m.sqrt(rap-Rmean),
                                               args=(E,L,self._2dpot,
                                                     rap),
                                               **kwargs))[0]
        elif Rmean < rap and fixed_quad:
            Tr+= integrate.fixed_quad(_TrSphericalIntegrandLarge,
                                      0.,m.sqrt(rap-Rmean),
                                      args=(E,L,self._2dpot,
                                            rap),
                                      n=10,**kwargs)[0]
        Tr= 2.*Tr
        return 2.*nu.pi/Tr

    def _calc_op(self,Or,Rmean,rperi,rap,E,L,fixed_quad,**kwargs):
        #Azimuthal period
        I= 0.
        if Rmean > rperi and not fixed_quad:
            I+= nu.array(integrate.quadrature(_ISphericalIntegrandSmall,
                                              0.,m.sqrt(Rmean-rperi),
                                              args=(E,L,self._2dpot,
                                                    rperi),
                                              **kwargs))[0]
        elif Rmean > rperi and fixed_quad:
            I+= integrate.fixed_quad(_ISphericalIntegrandSmall,
                                     0.,m.sqrt(Rmean-rperi),
                                     args=(E,L,self._2dpot,rperi),
                                     n=10,**kwargs)[0]
        if Rmean < rap and not fixed_quad:
            I+= nu.array(integrate.quadrature(_ISphericalIntegrandLarge,
                                              0.,m.sqrt(rap-Rmean),
                                              args=(E,L,self._2dpot,
                                                    rap),
                                              **kwargs))[0]
        elif Rmean < rap and fixed_quad:
            I+= integrate.fixed_quad(_ISphericalIntegrandLarge,
                                     0.,m.sqrt(rap-Rmean),
                                     args=(E,L,self._2dpot,rap),
                                     n=10,**kwargs)[0]
        I*= 2*L
        return I*Or/2./nu.pi

    def _calc_long_asc(self,z,R,axivz,phi,Lz,L):
        i= nu.arccos(Lz/L)
        sinu= z/R/nu.tan(i)
        pindx= (sinu > 1.)*(sinu < (1.+10.**-7.))
        sinu[pindx]= 1.
        pindx= (sinu < -1.)*(sinu > (-1.-10.**-7.))
        sinu[pindx]= -1.           
        u= nu.arcsin(sinu)
        vzindx= axivz > 0.
        u[vzindx]= nu.pi-u[vzindx]
        return phi-u
    
    def _calc_angler(self,Or,r,Rmean,rperi,rap,E,L,vr,fixed_quad,**kwargs):
        if r < Rmean:
            if r > rperi and not fixed_quad:
                wr= Or*integrate.quadrature(_TrSphericalIntegrandSmall,
                                            0.,m.sqrt(r-rperi),
                                            args=(E,L,self._2dpot,rperi),
                                            **kwargs)[0]
            elif r > rperi and fixed_quad:
                wr= Or*integrate.fixed_quad(_TrSphericalIntegrandSmall,
                                            0.,m.sqrt(r-rperi),
                                            args=(E,L,self._2dpot,rperi),
                                            n=10,**kwargs)[0]
            else:
                wr= 0.
            if vr < 0.: wr*= -1.
        else:
            if r < rap and not fixed_quad:
                wr= Or*integrate.quadrature(_TrSphericalIntegrandLarge,
                                            0.,m.sqrt(rap-r),
                                            args=(E,L,self._2dpot,rap),
                                            **kwargs)[0]
            elif r < rap and fixed_quad:
                wr= Or*integrate.fixed_quad(_TrSphericalIntegrandLarge,
                                            0.,m.sqrt(rap-r),
                                            args=(E,L,self._2dpot,rap),
                                            n=10,**kwargs)[0]
            else:
                wr= m.pi
            if vr < 0.:
                wr= m.pi+wr
            else:
                wr= m.pi-wr
        return wr
        
    def angle2(self,**kwargs):
        """
        NAME:
           angle2 DONE
        PURPOSE:
           Calculate the longitude of the ascending node
        INPUT:
        OUTPUT:
           angle2 in radians + 
           estimate of the error
        HISTORY:
           2011-03-03 - Written - Bovy (NYU)
        """
        if hasattr(self,'_angle2'): return self._angle2
        if not hasattr(self,'_i'): self._i= m.acos(self._J1/self._J2)
        if self._i == 0.: dstdj2= m.pi/2.
        else: dstdj2= m.asin(m.cos(self._theta)/m.sin(self._i))
        out= self._angle3(**kwargs)*self.T3(**kwargs)[0]/self.T2(**kwargs)[0]
        out[0]+= dstdj2
        #Now add the final piece dsrdj2
        EL= self.calcEL()
        E, L= EL
        Rmean= m.exp((m.log(rperi)+m.log(rap))/2.)
        if self._axi._R < Rmean:
            if self._axi._R > self.rperi:
                out+= L*nu.array(integrate.quadrature(_ISphericalIntegrandSmall,
                                                      0.,m.sqrt(self._axi._R-rperi),
                                                      args=(E,L,self._pot,rperi),
                                                      **kwargs))
        else:
            if self._axi._R < self._rap:
                out+= L*nu.array(integrate.quadrature(_ISphericalIntegrandLarge,
                                                      0.,m.sqrt(rap-self._axi._R),
                                                      args=(E,L,self._pot,rap),
                                                      **kwargs))
            else:
                out[0]+= m.pi*self.T3(**kwargs)[0]/self.T2(**kwargs)[0]
        if self._axi._vR < 0.:
            out[0]+= m.pi*self.T3(**kwargs)[0]/self.T2(**kwargs)[0]
        self._angle2= out
        return self._angle2

def _JrSphericalIntegrand(r,E,L,pot):
    """The J_r integrand"""
    return nu.sqrt(2.*(E-potentialAxi(r,pot))-L**2./r**2.)

def _TrSphericalIntegrandSmall(t,E,L,pot,rperi):
    r= rperi+t**2.#part of the transformation
    return 2.*t/_JrSphericalIntegrand(r,E,L,pot)

def _TrSphericalIntegrandLarge(t,E,L,pot,rap):
    r= rap-t**2.#part of the transformation
    return 2.*t/_JrSphericalIntegrand(r,E,L,pot)

def _ISphericalIntegrandSmall(t,E,L,pot,rperi):
    r= rperi+t**2.#part of the transformation
    return 2.*t/_JrSphericalIntegrand(r,E,L,pot)/r**2.

def _ISphericalIntegrandLarge(t,E,L,pot,rap):
    r= rap-t**2.#part of the transformation
    return 2.*t/_JrSphericalIntegrand(r,E,L,pot)/r**2.
