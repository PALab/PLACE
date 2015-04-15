'''
Master script to run laser-ultrasound experiment using PLACE automation.

1. Instruments and scan parameters are initialized
2. Header is created
3. Scan: data is acquired, displayed, and appended to stream file for each stage position
  - Data is saved to an HDF5 file (e.g. filename.h5) in the same folder as Scan.py:
4. Connection to instruments are closed

@author: Jami L Johnson
March 19, 2015
'''

import sys
import os
# set permissions of RS-232 serial port for vibrometer control
os.system('sudo chmod -R 0777 /dev/ttyS0') 
os.system('sudo chmod a+rw /dev/ttyS0')
# set permissions of USB port for laser source
#os.system('sudo chmod -R 0777 /dev/ttyUSB0') # laser
#os.system('sudo chmod a+rw /dev/ttyUSB0')


from math import ceil, log
import matplotlib.pyplot as plt 
import numpy as np
from numpy import matrix
import getopt
import time
from obspy import read, Trace, UTCDateTime
from obspy.core.trace import Stats
from obspy.core import AttribDict
import re
import h5py
import obspyh5
from string import atoi
from time import sleep

# PLACE modules
import place.automate.osci_card.controller as card
from place.automate.xps_control.XPS_C8_drivers import XPS
from place.automate.polytec.vibrometer import Polytec, PolytecDecoder, PolytecSensorHead
from place.automate.quanta_ray.QRay_driver import QuantaRay, QSW, QRread, QRstatus, QRcomm
from place.automate.scan.scanFunctions import Initialize, Execute, Scan 

def main():

    # -----------------------------------------------------
    # process command line options
    # -----------------------------------------------------

    try:
        opts,args = getopt.getopt(sys.argv[1:], 'h',['help','s1=','s2=','scan=','sr=','tm=','ch=','av=','wt=','rv=','sl=','vch=','tl=','tr=','chr=','cp=','ohm=','i1=','d1=','f1=','i2=','d2=','f2=','n=','dd=','rg=','map=','en=','pp=','bp=','comments='])
    except getopt.error, msg:
        print msg
        print 'for help use --help'
        sys.exit(2)
 
    global instruments, par 

    par = Initialize().options(opts, args)
    
    # -----------------------------------------------------
    # Initialize instruments
    # -----------------------------------------------------

    instruments = []
 
    # Initialize XPS stage controller
    if par['SCAN'] == '1D':
        par = Initialize().controller('130.216.58.154',par,1)
        instruments.append(par['GROUP_NAME_1'])
    elif par['SCAN'] == '2D':
        instruments.append(par['GROUP_NAME_1'])
        instruments.append(par['GROUP_NAME_2'])
        par = Initialize().controller('130.216.58.154',par,1)
        par = Initialize().controller('130.216.58.154',par,2)    
    

    # Initialize and set header information for receiver
    if par['RECEIVER'] == 'polytec':
        par = Initialize().polytec(par)
        instruments.append('POLYTEC')
    elif par['RECEIVER'] == 'gclad':
        par['MAX_FREQ'] = '6MHz'
        par['MIN_FREQ'] = '50kHz'
        par['TIME_DELAY'] = 0
        par['DECODER'] = ''
        par['DECODER_RANGE'] = ''
        par['CALIB'] = '1'
        par['CALIB_UNIT'] = 'V'
    elif par['RECEIVER'] == 'osldv':
        par['MAX_FREQ'] = ''
        par['MIN_FREQ'] = ''
        par['TIME_DELAY'] = 0
        par['DECODER'] = ''
        par['DECODER_RANGE'] = ''
        par['CALIB'] = ''
        par['CALIB_UNIT'] = 'V'
        
    
    # Initialize oscilloscope card
    par = Initialize().osci_card(par)

    # Initialize Quanta-Ray source laser
    # traceTime = Initialize().quanta_ray(energy, averagedRecords)
    # instruments.append('QUANTA_RAY')

    par = Initialize().time(par)

    # -----------------------------------------------------
    # Initialize header
    # -----------------------------------------------------

    header = Initialize().header(par)
    
    # -----------------------------------------------------
    # Perform scan
    # -----------------------------------------------------
    
    if par['SCAN'] == '1D':
        Scan().oneD(par, header)
    elif par['SCAN'] == '2D':
        Scan().twoD(par, header)
    elif par['SCAN'] == 'point':
        Scan().point(par,header)
    else:
        print 'invalid scan type!'

    # -----------------------------------------------------
    # close instrument connections
    # -----------------------------------------------------
    Execute().close(instruments,par)
   
    exit()


if __name__ == "__main__":
    try:
        while(True):
            main()
    except KeyboardInterrupt:
        print 'Keyboard Interrupt!  Instrument connections closing...'
        Execute().close(instruments,par)