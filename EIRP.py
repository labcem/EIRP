# -*- coding: utf-8 -*-
"""
Created on Thu Nov 26 2015
Measurement with the anechoic room, EDF Lab bât D16
emmanuel.amador@edf.fr
"""

from __future__ import division
import time
import visa
import scipy
import os
from numpy import *
import matplotlib.pyplot as plt

#Instruments modules
import Spectrum
from FC06 import * #classe du mât et de la table tournante de la CA

nom=raw_input('Enter the name of the equipment: ')
if (os.path.isdir('Results_'+nom)==False):
    os.mkdir('Results_'+nom)
    
#Calibration files
Correction_H=loadtxt('Cal_Pol_H.txt')   
Correction_V=loadtxt('Cal_Pol_V.txt')

os.chdir('Results_'+nom)

f=Correction_V[:,0]

###############################################
##########   Testing parameters  ##############
###############################################

fstart=f[0]      #Start frequency
fstop=f[-1]       #Stop frequency
fcenter=0.5*(fstart+fstop)   #Center frequency       
fspan=fstop-fstart   #Span
RBW=1e6       #RBW size in Hz
VBW=100e3       #VBW size in Hz
SwpPt=len(f)       #Number of points

N=37      #Number of incident angles
Angles=linspace(0,360,N)-180
Pol=2       #Number of polarizations
Exp=1    #Number of cutting planes
Tmes=15     #dwell time

###Stop criterion
###channels center frequencies (european wifi)
##f0=2.412e9
##fn=2.472e9
##n=13 #number of channels
##fc=linspace(f0,fn,n)
###channel center frequencies indexes
##peaksindx=zeros(len(fc))
##for i in range(len(fc)):
#    peaksindx[i]=argmin(abs(f-fc[i]))
Level_criterion=-60

print '\nInstruments initializations\n'
print '\nSpectrum analyzer:'
Spectre=Spectrum.FSV30()
Spectre.reset()
Spectre.startFreq(fstart)    
Spectre.stopFreq(fstop)      
Spectre.RBW(RBW)             
Spectre.SweepPoint(SwpPt)    
Spectre.MaxHold()            
Spectre.UnitDBM()            

print u'\nFC-06 Mast and TurnTable Controller'
FC=FC06()
FC.reset()
FC.AngleVel(20)
#FC.hVel(20)
FC.setAngle(0)
print 'Full anechoic chamber, heigth=1.1 m'
FC.setHauteur(1100)

print '\nMeasurement...\n'
raw_input (u"Place your EUT, first cutting plane, angle 0°, Presse Enter ")               
Measurement=empty([Pol,Exp,N,2])
Raw_Traces=empty([Pol,Exp,N,2,SwpPt])

for k in range(Exp):
    if k!=0:
        print (u"\nBack to 0°")
        FC.setAngle(0)
        raw_input ("Place your object according to cutting plane %s, Presse Enter " %(k+1))
    for l in range (0,Pol):
        if l==0:
            Polarization='V'
        else:
            Polarization='H'
        FC.setPolar(l)
        while FC.busy()=="1":
            #print("NOK")
            time.sleep(0.2)
        print("OK")
        print("Cutting plane : %i, antenna polarization : %s " %(k+1,Polarization))
        for j in range(0,len(Angles)):              
            #print ("Go to %s deg" %(Angles [j]))
            FC.setAngle(int(Angles[j]))
            Spectre.readwrite()
            Spectre.MaxHold()                   
            time.sleep(Tmes)                    
            #raw_input("\n Press Enter to validate the measurement\n")
            Level = Spectre.getTrace(SwpPt)    
            if Polarization=='V':
                cLevel=Level+Correction_V[:,1]
            else:                    
                cLevel=Level+Correction_H[:,1]
            #criterion automatic stop
            #while (min(Level[peaksindx])<Level_criterion): #every channel
            #while (min(Level[peaksindx])<Level_criterion): #one channel
            #while (mean(Level[peaksindx]<Level_criterion))<p/n: #p channels among n
            while (max(Level)<Level_criterion):
                Level = Spectre.getTrace(SwpPt)    
                if Polarization=='V':
                    cLevel=Level+Correction_V[:,1]
                else:                    
                    cLevel=Level+Correction_H[:,1]
                time.sleep(Tmes)
            Trace=Level     
            MaxLevel=max(cLevel)           
            MaxIdx =cLevel.argmax()             
            Measurement[l,k,j,:]=array([f[MaxIdx],MaxLevel])
            Raw_Traces[l,k,j,:]=Trace
            print u'%s°, EIRP = %2.2f mW/MHz' %((Angles [j]),10**(MaxLevel/10))
        fname = ( '%s_Exp%s.txt')  %(Polarization,k+1)
        savetxt(fname,Measurement[l,k,:])
    r=sum((10**((Measurement[:,k,:,1])/10)),axis=0)           
    print "Printing some figures..."    
    plt.close('all')        
    plt.polar((Angles*pi/180),r)
    Graphlin= 'Graph_Exp%s' %(k+1)
    plt.ylabel('PIRE/mW')
    plt.title("PIRE en mW, plan %s" %(k+1))
    plt.savefig(Graphlin+'.pdf',bbox='tight')
    plt.savefig(Graphlin+'.png',bbox='tight')
    print (Graphlin+'.pdf')
    print (Graphlin+'.png')    
    plt.close()
print "Raw data saved in file "+nom+'_raw.npz'
savez(nom+'_raw.npz',Measurement=Measurement,Raw_Traces=Raw_Traces,f=f)

print(u"Back to 0° and vertical polarization ")
FC.setAngle(0)
FC.setPolar(0)
print("OK")
