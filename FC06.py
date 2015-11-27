# -*- coding: utf-8 -*-
"""
Created on Wed Nov 04 16:36:25 2015

@author: Administrateur
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
        
    #### Plateau Tournant    
    def getAngle(self):
        """ Angle du plateau tournant"""
        return self.ctrl.ask("POS:ANGL?")
        
    def AngleVel(self,value):
        """ vitesse de rotation..."""
        time.sleep(0.5)
        if value<=self.vanglemax and value>=self.vanglemin:
            self.ctrl.write("POS:ANGL:VEL %s" %value)
            s="1"
            while s=="1":
                time.sleep(0.5)
                s=self.ctrl.ask("*BUSY?")
        else:
            print("vitesse angulaire non valide")
        return True
    
    def setAngle(self,value):
        """ aller à l'angle..."""
        time.sleep(0.5)
        if value<=self.anglemax and value>=self.anglemin:
            self.ctrl.write("POS:ANGL %s" %value)
            s="1"
            while s=="1":
                time.sleep(0.5)
                s=self.ctrl.ask("*BUSY?")
        else:
            print("angle non valide")
        return True
        
    #### Mât d'antenne
    def getHauteur(self):
        """ Hauteur de l'antenne"""
        return self.ctrl.ask("POS ?")
        
    def hVel(self,value):
        """ vitesse du mat..."""
        time.sleep(0.5)
        if value<=self.vhmax and value>=self.vhmin:
            self.ctrl.write("POS:VEL %s" %value)
            s="1"
            while s=="1":
                time.sleep(0.1)
                s=self.ctrl.ask("*BUSY?")
        else:
            print("vitesse non valide")
        return True
    
    def setHauteur(self,value):
        """ aller à la hauteur d'antenne..."""
        time.sleep(0.5)
        if value<=self.hmax and value>=self.hmin:
            self.ctrl.write("POS %s" %value)
            s="1"
            while s=="1":
                time.sleep(0.5)
                s=self.ctrl.ask("*BUSY?")
        else:
            print("hauteur non valide")
        #return True    
    
    def getPolar(self):
        """ Polarisation de l'antenne"""
        s=self.ctrl.ask("POL ?")
        if s=="90.0":
            ans="Polarisation Horizontale"
        if s=="0.0":
            ans="Polarisation Verticale"
        #print(ans)
        return ans
    
    def setPolar(self,value):
        """ définit la polarisation de l'antenne...
        value=1 si verticale
        value=0 si horizontale
        
        """
        time.sleep(0.5)
        if value!=0 and value!=1:
            print("polarisation non valide")
        else:
            if value==1:
                self.ctrl.write("POL VERT")
            if value==0:
                self.ctrl.write("POL HOR")
            s="1"
            while s=="1":
                time.sleep(0.5)
                s=self.ctrl.ask("*BUSY?")
        return True
        
    def busy(self):
        """ dit si la table ou nle mat bougent
        value=1 si ACTIF
        value=0 sinon
        
        """
        s=self.ctrl.ask("*BUSY?")
        return s   


        