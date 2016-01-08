# -*- coding: utf-8 -*-
"""
Created on Tue Apr 30 14:25:50 2013

This program returns a 2 columns txt file with frequency|Attenaution of the cable
The txt file can be loaded in "Calibration_without_Cable_losses_measurement.py"
and the attenuation are dervided by using a linear interpolation for the tested frequencies.@author: emmanuel.amador@edf.fr
"""

from __future__ import division
import time
import os
from numpy import *
import visa
from pylab import *

#Instrument modules
import Spectrum
import SignalGenerator

test_name = raw_input('Enter the name of the calibration: ')   
if os.path.isdir('CableLoss_'+test_name)==False:            #verify if the folder exists
   os.mkdir('CableLoss_'+test_name)			    #create the folder
    
os.chdir('CableLoss_'+test_name)


###############################################
##########   Testing parameters  ##############
###############################################

fstart=2.40e6      #start frequency
fstop=2.5e9       #stop frequency
fcenter=0.5*(fstart+fstop)   #center frequency        
fspan=fstop-fstart   #Span
RBW=1e6      #RBW size in Hz
VBW=100e3       #VBW size in Hz
SwpPt=101       #number of points
f=linspace(fstart,fstop,SwpPt) #frequency points

#f=[f0]
#rho=1.01
#i=1
#while f[i-1] <f1:
#    fi=[fi-1]*rho
#    f=append(f,fi)    
#    i+=1

#Power level
P0=-20  

###############################################
######  Instruments  Initialiations  ##########
###############################################
print '\nInitialisations\n'
print '\n Signal generator init.'
gene=SignalGenerator.RS_SMF100A()
gene.reset()
gene.off() #RF OFF
gene.setPower(P0)
gene.setFreq(fcenter)

print '\nSpectrum analyser:'
Spectre=Spectrum.FSV30()
Spectre.reset()
Spectre.RBW(RBW)
Spectre.SweepPoint(SwpPt)    
Spectre.UnitDBM()            
Spectre.SPAN(fspan)
Spectre.centerFreq(fcenter)

print 'OK\n'

###############################################
############# Measurement #####################
###############################################
PuissanceInj=zeros(len(f)) #Injected Power table 
PuissanceMes=zeros(len(f)) #Measured power table 
Measurement=zeros((len(f),2))

gene.on()
for j in range(0,len(f)): #loop over the frequencies
    Spectre.centerFreq(fcenter)
    gene.setFreq(f[j])
    gene.setPower(P0)
    time.sleep(0.1)
    Trace = Spectre.getTrace(SwpPt)
    #time.sleep(0.2)   
    PuissanceInj[j]=P0
    PuissanceMes[j]=max(Trace) #MarkerValue
    Measurement[j,:]=array([f[j],PuissanceMes[j]-PuissanceInj[j]])
    print 'f = %2.2f MHz, Losses = %2.2f dB' %(f[j]/1e6,Measurement[j,1])
gene.off()
    
fname ='CableLoss_'+test_name+'.txt'  

fnamez = fname + '.npz'
savez(test_name,f=f,PuissanceInj=PuissanceInj,PuissanceMes=PuissanceMes)
print 'Saving in txt file...' 
savetxt(fname,Measurement[1:,:])
os.chdir("..")
savetxt(fname,Measurement[1:,:])
print 'OK'



