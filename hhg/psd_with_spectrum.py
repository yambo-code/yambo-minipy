#!/usr/bin/python
from scipy import signal
import numpy as np
import matplotlib.pyplot as plt
from math import pi
import argparse
import re


"""
Simple way to calculate the power-spectra using Numpy
Author:  C. Attaccalite
"""

#
# parse command line
#
parser = argparse.ArgumentParser(prog='simple_ps',description='Simple way to calculate power spectra',epilog="Copyright C. Attaccalite")
parser.add_argument('-f', help="current file",type=str , default=None, dest="curr_fname")
parser.add_argument('-d', help="direction (x=1,y=2,z=3)",type=int , default='1', dest="idir")
args = parser.parse_args()

print("\n * * * Calculation of power spectra from time-dependent current * * * \n\n")

args = parser.parse_args()

if args.curr_fname == None:
    print('type "simple_ps.py --help" for help ',)
    exit(0)

# Read laser frequency
try:
    curr_file=open(args.curr_fname,"r")
except Exception as e:
    print("Error opening file!")
    print(e)
    exit(0)

lines=curr_file.read()

decimal  =r'(-?\d+\.\d*|-?\.\d+)'
pattern=r'Frequency value\s*'+decimal+'\s*'

try:
    match = re.search(pattern, lines, re.MULTILINE)
    lfreq = float(match.group(1))
except Exception as e:
    print("Error reading laser frequency!")
    print(e)
    exit(0)

curr_file.close()
print("Laser frequency: %13.8f \n" % lfreq)

data=np.genfromtxt(args.curr_fname,comments="#")
plt.figure()
plt.title('Signal')
plt.xlabel('Time [fs]')
plt.plot(data[:,0],data[:,args.idir])

f, Pxx_den = signal.periodogram(data[:,args.idir],1.0/(data[1,0]-data[0,0]),scaling='spectrum')

# 1 hertz [Hz] = 4.13566553853599E-15 electron-volt [eV]

f=f*4.1356655385

plt.figure()
plt.semilogy(f/lfreq, Pxx_den,label='Laser freq = '+str(lfreq)+' eV')
data=np.column_stack((f/lfreq,Pxx_den))
np.savetxt("psd.data",data)


plt.ylim([1e-34, 10e-14])
plt.xlim([0.1,30])
plt.xlabel('Harmonic number')
plt.ylabel(r"PSD $\left[\frac{V^2}{Hz}\right]$")
plt.legend()
plt.savefig("psd.pdf")
plt.show()
