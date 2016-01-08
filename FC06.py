# -*- coding: utf-8 -*-
"""
Created on Wed Nov 04 16:36:25 2015

This class controls the FC-06 controller for the mast and turnin table.
Beware of the controller, sometimes it does not appear as an instrument in the GPIB chain.
You have to be careful with the GPIB cables and wait a bit before trying to send commands.
Do not forget to switch on the mast in the chamber before the controller.

If nothing is moving go to http://192.168.100.10:8040/webvisu.htm with IE and try
to change the velocities of the mast and the turning tables, or try to move them
with the web interface.

@author: emmanuel.amador@edf.fr
"""

from visa import instrument
from numpy import *
import time

class FC06():
    def __init__(self,address=15):
        self.ctrl = instrument("GPIB::%s" %address,timeout=None)
        self.vanglemax=30
        self.vanglemin=1
        self.anglemax=200
        self.anglemin=-200
        self.hmax=2000
        self.hmin=1000
        self.vhmax=30
        self.vhmin=1
    def reset(self):
        """ RESET """
        self.ctrl.write("*RST")
    
    def idn(self):
        """ *IDN? """
        s=self.ctrl.ask("*IDN?")
        print(s)
        return True
        
    def busy(self):
        """ dit si la table ou le mat bougent
        value=1 si ACTIF
        value=0 sinon
        """
        s=self.ctrl.ask("*BUSY?")
        return s   

        
    #### Turning table   
    def getAngle(self):
        """ get the actual angle the turning table """
        return self.ctrl.ask("POS:ANGL?")
        
    def AngleVel(self,value):
        """ set the angular velocity of the turning table..."""
        time.sleep(0.5)
        if value<=self.vanglemax and value>=self.vanglemin:
            self.ctrl.write("POS:ANGL:VEL %s" %value)
            s="1"
            while s=="1":
                time.sleep(0.5)
                s=self.ctrl.ask("*BUSY?")
        else:
            print("out of range angular velocity")
        return True
    
    def setAngle(self,value):
        """ turn the turntable to the given angle..."""
        time.sleep(0.5)
        if value<=self.anglemax and value>=self.anglemin:
            self.ctrl.write("POS:ANGL %s" %value)
            s="1"
            while s=="1":
                time.sleep(0.5)
                s=self.ctrl.ask("*BUSY?")
        else:
            print("out of range angle")
        return True
        
    #### Antenna Mast
    def getHauteur(self):
        """ get the actual antenna height"""
        return self.ctrl.ask("POS ?")
        
    def hVel(self,value):
        """ set the vertical velocity of the mast (not working properly for some reason) """
        time.sleep(0.5)
        if value<=self.vhmax and value>=self.vhmin:
            self.ctrl.write("POS:VEL %s" %value)
            s="1"
            while s=="1":
                time.sleep(0.5)
                s=self.ctrl.ask("*BUSY?")
        else:
            print("out of range velocity")
        return True
    
    def setHauteur(self,value):
        """ got to heigth..."""
        time.sleep(0.5)
        if value<=self.hmax and value>=self.hmin:
            self.ctrl.write("POS %s" %value)
            s="1"
            while s=="1":
                time.sleep(0.5)
                s=self.ctrl.ask("*BUSY?")
        else:
            print("out of range height")
        #return True    
    
    def getPolar(self):
        """ get the actual antenna's polarisation"""
        s=self.ctrl.ask("POL ?")
        if s=="90.0":
            ans="Horizontal Polarisation"
        if s=="0.0":
            ans="Vertical Polarisation"
        return ans
    
    def setPolar(self,value):
        """ set the antenna's polarisation
        value=1 : vertical
        value=0 : horizontal
        
        """
        time.sleep(2)
        if value!=0 and value!=1:
            print("invalid polarisation")
        else:
            if value==1:
                self.ctrl.write("POL VERT")
            if value==0:
                self.ctrl.write("POL HOR")
            s="1"
            while s=="1":
                time.sleep(2)
                s=self.ctrl.ask("*BUSY?")
        return True
        


        
