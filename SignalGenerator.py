# -*- coding: utf-8 -*-
"""
Created on Fri Feb 22 10:45:00 2013
Signal generator control module
"""

from visa import instrument

class RS_SMF100A():
    def __init__(self,address=28):
        self.ctrl = instrument("GPIB::%s" %address)
        self.powmax=15
    
    def reset(self):
        """ RESET """
        self.ctrl.write("*RST;*WAI")
        self.ctrl.write("*ESE 1;*SRE 32;OUTP1 OFF")
        #self.ctrl.write(":AM:STAT OFF;:AM:SOUR INT")
        self.ctrl.write("PULM:SOUR INT;:PULM:STAT OFF")
        print 'OK'
        return True
    
    def off(self):
        """ RF OFF """
        return self.ctrl.write("*CLS;OUTP1 OFF")
    
    def on(self):
        """ RF ON """
        return self.ctrl.write("*CLS;OUTP1 ON")
    
    def setPower(self,value):
        """ set the output power level"""
        if value>self.powmax:
            print '!!!!!!!!!!!!!!!\n!!! POWER TOO HIGH !!!\n!!!!!!!!!!!!!!!!'
        else:
            self.ctrl.write("*CLS;POW %s dbm" %value)
        
    def setFreq(self,value):
        """ set the signal frequency"""
        s='"*CLS;FREQ '+str(int(value))+' HZ"'
        return self.ctrl.write("*CLS;FREQ %s HZ" %value)
