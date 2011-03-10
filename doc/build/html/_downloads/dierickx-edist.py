import sys
import os, os.path
import math as m
import numpy as nu
import csv
import cPickle as pickle
import galpy.util.bovy_plot as plot
from galpy.potential import MiyamotoNagaiPotential, HernquistPotential, NFWPotential, LogarithmicHaloPotential
from galpy.orbit import Orbit
_degtorad= nu.pi/180.
def calc_es():
    savefilename= 'myes.sav'
    if os.path.exists(savefilename):
        savefile= open(savefilename,'rb')
        mye= pickle.load(savefile)
        e= pickle.load(savefile)
        savefile.close()
    else:
       #Read data
        dialect= csv.excel
        dialect.skipinitialspace=True
        reader= csv.reader(open('../data/Dierickx-etal-tab2.txt','r'),delimiter=' ',dialect=dialect)
        vxvs= []
        es= []
        vphis= []
        vxs= []
        vys= []
        vzs= []
        ls= []
        for row in reader:
            thisra= float(row[3])
            thisdec= float(row[4])
            thisd= float(row[17])/1000.
            thispmra= float(row[13])
            thispmdec= float(row[15])
            thisvlos= float(row[11])
            thise= float(row[26])
            vxvs.append([thisra,thisdec,thisd,thispmra,thispmdec,thisvlos])
            es.append(thise)
            vphis.append(float(row[25]))
            vxs.append(float(row[19]))
            vys.append(float(row[21]))
            vzs.append(float(row[23]))
            ls.append(float(row[5]))
        vxvv= nu.array(vxvs)
        e= nu.array(es)
        vphi= nu.array(vphis)
        vx= nu.array(vxs)
        vy= nu.array(vys)
        vz= nu.array(vzs)
        l= nu.array(ls)

        #Define potential
        lp= LogarithmicHaloPotential(normalize=1.)
        mp= MiyamotoNagaiPotential(a=0.5,b=0.0375,amp=1.,normalize=.6)
        np= NFWPotential(a=4.5,normalize=.35)
        hp= HernquistPotential(a=0.6/8,normalize=0.05)
        ts= nu.linspace(0.,20.,10000)
        
        mye= nu.zeros(len(e))
        for ii in range(len(e)):
           #Integrate the orbit
            o= Orbit(vxvv[ii,:],radec=True,vo=220.,ro=8.)
            o.integrate(ts,lp)
            mye[ii]= o.e()
            

        #Save
        savefile= open(savefilename,'wb')
        pickle.dump(mye,savefile)
        pickle.dump(e,savefile)
        savefile.close()

    #plot
    plot.bovy_print()
    plot.bovy_plot(nu.array([0.,1.]),nu.array([0.,1.]),'k-',
                   xlabel=r'$\mathrm{Dierickx\ et\ al.}\ e$',
                   ylabel=r'$\mathrm{galpy}\ e$')
    plot.bovy_plot(e,mye,'k,',overplot=True)
    plot.bovy_end_print('myee.png')

    plot.bovy_print()
    plot.bovy_hist(e,bins=30,xlabel=r'$\mathrm{Dierickx\ et\ al.}\ e$')
    plot.bovy_end_print('ehist.png')

    plot.bovy_print()
    plot.bovy_hist(mye,bins=30,xlabel=r'$\mathrm{galpy}\ e$')
    plot.bovy_end_print('myehist.png')

if __name__ == '__main__':
    calc_es()
