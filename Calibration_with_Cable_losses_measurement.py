# -*- coding: utf-8 -*-
"""
Created on Wed Nov 25 2015
Calibration of the anechoic room, EDF Lab bât D16.
First this program measures the cable losses.

The program performs the free space "attenuation" measurement between the two antennas.
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

test_name = raw_input('Enter the name of the device: ')   
if os.path.isdir('CableLoss_'+test_name)==False:            #verify if the folder exists
   os.mkdir('CableLoss_'+test_name)			    #create the folder
    
os.chdir('CableLoss_'+test_name)


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

print 'Measurement of the cable\'s losses\n'
raw_input(u'\nConnect the 10 m cable to the spectrum analyser and press ENTER')



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

CableLoss=Measurement[:,1]

print 'Calibration of the chamber'
raw_input(u'\nConnect the 10 m cable to the emitting antenna\nand the receiving antenna back to the spectrum analyser, press ENTER')
if os.path.isdir('Calibration_'+test_name)==False:             #verify if the folder exists
   os.mkdir('Calibration_'+test_name)			       #create the folder
    
os.chdir('Calibration_'+test_name)


P_gene=0-CableLoss #Signal generator power to get 0 dBm at the antenna input
Pol=2       #Number of polarisations (vertical + horizontal = 2)

#Antenna gain (from calibration) interpolation for our measurement frequencies
Logper_AH=array([4.62,5.85,5.92,6.43,6.81,6.86,7.58,7.35,7.54,7.73,8.28,8.16,7.93,8.07,8.38,8.06,8.11,8.57,7.98,8.25,8.06,7.80,8.10,7.63])
G_ant_lin=transpose(array([linspace(1e9,12.5e9,24),10**(Logper_AH/10)]))    # frequency | Antenna gain (linear values)
G_ant_inter_lin=scipy.interp(f,G_ant_lin[:,0],G_ant_lin[:,1])   # interpolated gain (linear vlaues)
G_ant_inter_db=transpose(array([f,10*log10(G_ant_inter_lin)]))  # interpolated gain (dB)   

print u'\n FC-06 Mast and TurnTable Controller initialisation'
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


           
Calibration=empty([Pol,len(f),2])

for l in range (0,Pol):
    FC.setPolar(l)
    while FC.busy()=="1":
        time.sleep(0.2)
    print("OK")
    polar=FC.getPolar()
    raw_input(u'\n Emitting Antenna in %s polarisation? Press Entrer to continue' %(polar))
    SyntheseCal=zeros((len(f),2))
    print '%s' %(polar)  
    for i in range(0,len(f)):
        gene.setFreq(f[i])
        gene.setPower(P_gene[i])
        gene.on()
        time.sleep(0.05)       
        Niveau = Spectre.getTrace(SwpPt)
        MarkerValue=Niveau.max()
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
