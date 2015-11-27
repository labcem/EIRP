# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 12:57:09 2013
Spectrum Analyzer control class
"""

from visa import instrument
from numpy import *

class FSV30():
    def __init__(self,address=21):
        self.ctrl = instrument("GPIB::%s" %address)
      
    def reset(self):
        """ RESET """
        self.ctrl.write("*RST")
        self.ctrl.write(":INST SAN;*SRE 32;STATUS:PRESET")
        self.ctrl.write(":INP1:PRES ON")
        self.ctrl.write("DISP :TRAC:X:SPAC LIN;SCAN:RANG:COUN 1;INIT2:CONT OFF;INIT:IMM;*SRE 136;*ESE 64")
        self.ctrl.write("FORMAT:DATA REAL;*CLS;:CALC:UNIT:POW DBUV")
        self.ctrl.write(":CORR:TRANS OFF;:INIT:CONT ON;:SYST:DISP:UPD ON") 
        self.ctrl.write("FORM ASC")    
        print 'OK'
        return True
        
    def centerFreq(self,value):
        """ Center frequency"""
        return self.ctrl.write("FREQ:CENT %s HZ ;:INIT" %value)
       
    def startFreq(self,value):
        """ Start frequency"""
        return self.ctrl.write("FREQ:START %s HZ" %value)
        
    def stopFreq(self,value):
        """ Stop frequency"""
        return self.ctrl.write("FREQ:STOP %s HZ" %value)
        
    def SPAN(self,value):
        """ Span setting"""
        return self.ctrl.write("FREQ:SPAN %s HZ" %value)
        
    def RBW(self,value):
        """ RBW size setting"""
        return self.ctrl.write("BAND:RES %s Hz" %value)
        
        
    def VBW(self,value):
        """ VBW size setting"""
        return self.ctrl.write("BAND:VID %s Hz" %value)
        
    def Sweep(self,value):
        """ Sweep time setting"""
        return self.ctrl.write(":SWE:TIME:AUTO OFF;:SWE:TIME %s ms" %value)
      
    def MaxHold(self):
        """ Max Hold setting"""
        return self.ctrl.write("DISP:TRAC:MODE MAXH")
        
    def readwrite(self):
        """Mode READ/WRITE"""
        return self.ctrl.write("DISP:TRAC:MODE WRIT")
        
    def SweepPoint(self,value):
        """Number of points (between 101 and 32001)"""
        return self.ctrl.write("SWE:POIN %s" %value)
        
    def InputAtt(self,value):
        """ Input attenuator manual setting"""
        return self.ctrl.write("INP:ATT %s dB " %value)
        
    def InputAttAuto(self):
        """Input attenuator  automatic setting """
        return self.ctrl.write("INP:ATT:AUTO ON")
        
    def UnitDBM(self):
        """set unit in dBm"""
        return self.ctrl.write("UNIT:POW DBM")
        
    def getTrace(self,value):
        """ retrieve data """
        s=self.ctrl.ask("TRAC? TRACE1")  
        res=s.split(",")
        Data=zeros(value)
        for i in range(0,len(Data)):
            Data[i]=eval(res[i])
        return Data

    def MarkerMax(self,value):
        """ get the ax value"""
        self.ctrl.write("CALC:MARK1:X %s Hz" %value)
        MarkerValue=self.ctrl.ask("CALC:MARK1:Y?")
        return MarkerValue
        
        
    