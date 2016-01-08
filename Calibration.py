# -*- coding: utf-8 -*-
"""
Created on Wed Nov 25 2015
Calibration of the anechoic room, EDF Lab bât D16.

The program performs the free space "attenuation" measurement between the two antennas with a single cable loss value.
The program returns 2 files "Cal_Pol_V.txt" and "Cal_Pol_H.txt" at the root folder.
These files are needed to perform an EIRP measurement.

emmanuel.amador@edf.fr
"""
from __future__ import division
import scipy
from numpy import *
import os
import time
import visa

#Instrument modules
import Spectrum
import SignalGenerator
from FC06 import * #classe du mât et de la table tournante de la CA

test_name = raw_input('Enter the name of the calibration?')   
if os.path.isdir('Calibration_'+test_name)==False:            #verify if the folder exists
   os.mkdir('Calibration_'+test_name)						#create the folder
    
os.chdir('Calibration_'+test_name)

###############################################
##########   Testing parameters  ##############
###############################################

fstart=2.4e9      #start frequency
fstop=2.5e9       #stop frequency
fcenter=0.5*(fstart+fstop)   #center frequency        
fspan=fstop-fstart   #Span
RBW=1e6      #RBW size in Hz
VBW=100e3       #VBW size in Hz
SwpPt=1001       #number of points
f=linspace(fstart,fstop,SwpPt) #frequency points

Pol=2       #Number of polarisations (vertical + horizontal = 2)
CableLoss=4.1 # Cable loss in dB
P_gene=0+CableLoss #Signal generator power to get 0 dBm at the antenna input

#Antenna gain (from calibration) interpolation for our measurement frequencies
Logper_AH=array([4.62,5.85,5.92,6.43,6.81,6.86,7.58,7.35,7.54,7.73,8.28,8.16,7.93,8.07,8.38,8.06,8.11,8.57,7.98,8.25,8.06,7.80,8.10,7.63])
G_ant_lin=transpose(array([linspace(1e9,12.5e9,24),10**(Logper_AH / 20)]))    # frequency | Antenna gain (linear values)
G_ant_inter_lin=scipy.interp(f,G_ant_lin[:,0],G_ant_lin[:,1])   # interpolated gain (linear vlaues)
G_ant_inter_db=transpose(array([f,20*log10(G_ant_inter_lin)]))  # interpolated gain (dB)   

print '\nInstruments initialisations\n'
print '\nSpectrum analyser:'
Spectre=Spectrum.FSV30()
Spectre.reset()
Spectre.RBW(RBW)
Spectre.SweepPoint(SwpPt)    
Spectre.UnitDBM()            
Spectre.SPAN(fspan)
Spectre.centerFreq(fcenter)


print '\nSignalGenerator:'
gene=SignalGenerator.RS_SMF100A()
gene.reset()
gene.off() #RF OFF
gene.setPower(P_gene)
gene.setFreq(fcenter)

print u'\n FC-06 Mast and TurnTable Controller'
FC=FC06()
FC.reset()
FC.AngleVel(20)
#FC.hVel(20)


#######Antenna height

#print '\n Optimisation of the height (maximum emission) ' #necessary in semi anechoic configuration
#print u'\n TurnTable toward O°'
#FC.setAngle(int(0))
#print u'\nVertical polarisation'
#FC.setPolar(0)
#while FC.busy()=="1":
#        #print("NOK")
#        time.sleep(0.2)
#print("OK")
#raw_input ('\n Emitting and receiving antennas both in vertical polarisation ? Press Entrer to continue')
#hmax=2000
#hmin=1000
#pas=10 #10 mm
#hauteur=arange(hmin,hmax+pas,pas)
#gene.on()
#mesure_max=zeros(len(hauteur))
#for i in range(len(hauteur)):
#    FC.setHauteur(int(hauteur[i]))
#    time.sleep(0.05) 
#    mesure_max[i]=(Spectre.getTrace(SwpPt)).max()
#    print (' Height = %2.2f mm, Power received = %2.2f dBm')  %(hauteur[i],mesure_max[i])
#gene.off()
#h_max=hauteur[argmax(mesure_max)]
#
#print ('Best Heigth = %2.2f mm')  %(h_max)
#print '\nBack to optimal height'     
#
#FC.setHauteur(int(h_max))

FC.setHauteur(1200) #1.2m in full anechoic configuration
  
print '\nCalibration of the chamber...\n'

           
Calibration=empty([Pol,len(f),2])

for l in range (0,Pol):
    FC.setPolar(l)
    while FC.busy()=="1":
        #print("NOK")
        time.sleep(0.2)
    print("OK")
    polar=FC.getPolar()
    raw_input(u'\n Emitting Antenna in %s polarisation? Press Entrer to continue' %(polar))
    SyntheseCal=zeros((len(f),2))
    print '%s' %(polar)  
    for i in range(0,len(f)):
        gene.setFreq(f[i])
        gene.on()
        time.sleep(0.05)       
        Niveau = Spectre.getTrace(SwpPt)
        MarkerValue=Niveau.max()#Spectre.MarkerMax(f[i])
        Correction=(0+G_ant_inter_db[i,1]-float(MarkerValue))
        SyntheseCal[i,:]=array([f[i],Correction])
        Calibration[l,i,:]=array([f[i],Correction])
        print ("f=%2.5f MHz, C=%2.2f dB") %(f[i]/1e6,Correction)
    fname = ('Cal_Pol_%s.txt')  %(polar[13:14]) 
    savetxt(fname,SyntheseCal[0:,:])
    savetxt("../"+fname,SyntheseCal[0:,:])
fnamez = 'Calibration_%s.npz' %test_name
savez(fnamez,Calibration=Calibration,f=f)        
      
gene.off() 
