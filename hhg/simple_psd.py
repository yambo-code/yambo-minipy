#!/usr/bin/python
from scipy import signal
import numpy as np
import matplotlib.pyplot as plt
import argparse


"""
Simple way to calculate the power-spectra using Numpy
Author:  C. Attaccalite
"""

#
# parse command line
#
parser = argparse.ArgumentParser(prog='simple_psd',description='Simple way to calculate power spectra density',epilog="Copyright C. Attaccalite")
parser.add_argument('-f', help="current file",type=str , default=None, dest="curr_fname")
parser.add_argument('-d', help="direction (x=1,y=2,z=3)",type=int , default='1', dest="idir")
args = parser.parse_args()

print("\n * * * Calculation of power spectra from time-dependent current * * * \n\n")

args = parser.parse_args()

if args.curr_fname == None:
    print('type "simple_ps.py --help" for help ',)
    exit(0)

data=np.genfromtxt(args.curr_fname,comments="#")
plt.figure()
plt.title('Signal')
plt.plot(data[:,0],data[:,args.idir])

np.fft.fft
freqs = np.fft.fftfreq(data[:,0].size, 1.0/(data[1,0]-data[0,0]))
idx = np.argsort(freqs)
ps = np.abs(np.fft.fft(data[:,args.idir]))**2
plt.figure()
plt.plot(freqs[idx], ps[idx])
plt.title('Power spectrum (np.fft.fft)')
plt.show()
