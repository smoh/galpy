###############################################################################
#   MovingObjectPotential.py: class that implements the potential coming from
#                             a moving object
###############################################################################
import copy
import numpy as nu
import warnings
from .Potential import Potential, _APY_LOADED, _isNonAxi, flatten, \
    evaluatePotentials, evaluateRforces, evaluatezforces, evaluateDensities, \
    evaluatephiforces
from .PlummerPotential import PlummerPotential
if _APY_LOADED:
    from astropy import units
from .ForceSoftening import PlummerSoftening
from galpy.util import galpyWarning
class MovingObjectPotential(Potential):
    """
    Class that implements the potential coming from a moving object by combining
    any galpy potential with an integrated galpy orbit.
    """
    def __init__(self,orbit,pot=None,amp=1.0,
                 ro=None,vo=None
                 ):
        """
        NAME:

           __init__

        PURPOSE:

           initialize a MovingObjectPotential

        INPUT:

           orbit - the Orbit of the object (Orbit object)

           pot - A potential object or list of potential objects (default: PlummerPotential with amp=0.06 and b=0.01)
           
           amp - amplitude

           ro=, vo= distance and velocity scales for translation into internal units (default from configuration file)

        OUTPUT:

           (none)

        HISTORY:

           2011-04-10 - Started - Bovy (NYU)

        """

        Potential.__init__(self,amp=amp,ro=ro,vo=vo)
        
        # If no potential supplied implement the default Plummer sphere
        if pot==None:
            pot=PlummerPotential(amp=0.06,b=0.01)
            self._pot = pot
        else:
            pot=flatten(pot)
            if _isNonAxi(pot):
                raise NotImplementedError('MovingObjectPotential for non-axisymmetric potentials is not currently supported')
            self._pot=pot
        self._orb= copy.deepcopy(orbit)
        self._orb.turn_physical_off()
        self.isNonAxi= True
        return None

    def _evaluate(self,R,z,phi=0.,t=0.):
        """
        NAME:
           _evaluate
        PURPOSE:
           evaluate the potential at R,z, phi
        INPUT:
           R - Galactocentric cylindrical radius
           z - vertical height
           phi - azimuth
           t - time
        OUTPUT:
           Phi(R,z,phi)
        HISTORY:
           2010104-10 - Started - Bovy (NYU)
        """
        #Cylindrical distance
        Rdist = _cylR(R,phi,self._orb.R(t),self._orb.phi(t))
        #Evaluate potential
        return evaluatePotentials( self._pot, Rdist, self._orb.z(t)-z, use_physical=False)

    def _Rforce(self,R,z,phi=0.,t=0.):
        """
        NAME:
           _Rforce
        PURPOSE:
           evaluate the radial force for this potential
        INPUT:
           R - Galactocentric cylindrical radius
           z - vertical height
           phi - azimuth
           t - time
        OUTPUT:
           the radial force
        HISTORY:
           2011-04-10 - Written - Bovy (NYU)
        """
        #Cylindrical distance
        Rdist = _cylR(R,phi,self._orb.R(t),self._orb.phi(t))
        # Difference vector
        (xd,yd,zd) = _cyldiff(self._orb.R(t), self._orb.phi(t), self._orb.z(t),
            R, phi, z)
        #Evaluate cylindrical radial force
        RF = evaluateRforces(self._pot,Rdist,zd, use_physical=False)
        # Return R force, negative of radial vector to evaluation location.
        return -RF*(nu.cos(phi)*xd+nu.sin(phi)*yd)/Rdist

    def _zforce(self,R,z,phi=0.,t=0.):
        """
        NAME:
           _zforce
        PURPOSE:
           evaluate the vertical force for this potential
        INPUT:
           R - Galactocentric cylindrical radius
           z - vertical height
           phi - azimuth
           t - time
        OUTPUT:
           the vertical force
        HISTORY:
           2011-04-10 - Written - Bovy (NYU)
        """
        #Cylindrical distance
        Rdist = _cylR(R,phi,self._orb.R(t),self._orb.phi(t))
        # Difference vector
        (xd,yd,zd) = _cyldiff(self._orb.R(t), self._orb.phi(t), self._orb.z(t),
            R, phi, z)
        #Evaluate and return z force
        return -evaluatezforces(self._pot,Rdist,zd, use_physical=False)

    def _phiforce(self,R,z,phi=0.,t=0.):
        """
        NAME:
           _phiforce
        PURPOSE:
           evaluate the azimuthal force for this potential
        INPUT:
           R - Galactocentric cylindrical radius
           z - vertical height
           phi - azimuth
           t - time
        OUTPUT:
           the azimuthal force
        HISTORY:
           2011-04-10 - Written - Bovy (NYU)
        """
        #Cylindrical distance
        Rdist = _cylR(R,phi,self._orb.R(t),self._orb.phi(t))
        # Difference vector
        (xd,yd,zd) = _cyldiff(self._orb.R(t), self._orb.phi(t), self._orb.z(t),
            R, phi, z)
        #Evaluate cylindrical radial force.
        RF = evaluateRforces(self._pot, Rdist, zd, use_physical=False)
        # Return phi force, negative of phi vector to evaluate location
        return -RF*R*(nu.cos(phi)*yd-nu.sin(phi)*xd)/Rdist

    def _dens(self,R,z,phi=0.,t=0.):
        """
        NAME:
           _dens
        PURPOSE:
           evaluate the density for this potential
        INPUT:
           R - Galactocentric cylindrical radius
           z - vertical height
           phi - azimuth
           t - time
        OUTPUT:
           the density
        HISTORY:
           2010-08-08 - Written - Bovy (NYU)
        """
        #Cylindrical distance
        Rdist = _cylR(R,phi,self._orb.R(t),self._orb.phi(t))
        # Difference vector
        (xd,yd,zd) = _cyldiff(self._orb.R(t), self._orb.phi(t), self._orb.z(t),
            R, phi, z)
        # Return the density
        return evaluateDensities(self._pot, Rdist, zd, use_physical=False)

def _cylR(R1,phi1,R2,phi2):
    return nu.sqrt(R1**2.+R2**2.-2.*R1*R2*nu.cos(phi1-phi2)) # Cosine law

def _cyldiff(R1,phi1,z1,R2,phi2,z2):
    dx = R1*nu.cos(phi1)-R2*nu.cos(phi2)
    dy = R1*nu.sin(phi1)-R2*nu.sin(phi2)
    dz = z1-z2
    return (dx,dy,dz)
