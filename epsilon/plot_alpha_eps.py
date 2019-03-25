#!/usr/bin/python
import argparse
import numpy as np
import sys
import math


def lorentzian(omega,gamma):
        return -gamma/(1j*omega-gamma)

"""
Contact excitation model
use the contact excitation model to correct the EPS
see eq. 8.3 in "Time-dependent density-functional theory for extended systems"
Reports on Progress in Physics, 70(3), 357.
Botti, S., Schindlmayr, A., Del Sole, R., & Reining, L. (2007). 
Author:  Claudio Attaccalite
"""
#
# parse command line
#
parser = argparse.ArgumentParser(prog='plot_alpha_eps',description='Correct the dielectric constant with the contact model',epilog="Copyright Claudio Attaccalite 2015")
parser.add_argument('-eps', help='File name of the dielectric constant (from ypp_rt)',dest="epsfile",type=str, required=True)
parser.add_argument('-a', help='Alpha',type=float,default=False,dest="alpha")
parser.add_argument('-s', help='Smearing',type=float,default=False,dest="smear")
args = parser.parse_args()

print("\n\n\n Contact excitonic model \n\n ")
print("Alpha = %f " % args.alpha)
try:
    EPS = np.genfromtxt(args.epsfile,comments="#")
except:
    print("Error opening the dielectric constant! ")
    sys.exit(1)

npts=EPS.shape[0]
print("Number of points in epsilon: %d " % (npts))

XHI0  =np.zeros(npts, dtype=complex)
XHI   =np.zeros(npts, dtype=complex)
EPS_C =np.zeros(npts, dtype=complex)

XHI0[0:npts-1] =EPS[0:npts-1,2]+EPS[0:npts-1,1]*1j - 1.0 

XHI[0:npts-1]  =XHI0[0:npts-1]/(1.0 + args.alpha*XHI0[0:npts-1]/(4.*math.pi))

dE=EPS[1,1]-EPS[0,1]
    
#if args.smear != 0:
#    test=open("test-smearing.dat","w")
#    for iw in xrange(-npts+1,npts-1):
#        line=" %.4g     %.4g        %.4g \n" % (iw*dE,lorentzian(dE*float(iw),args.smear).real,lorentzian(dE*float(iw),args.smear).imag) 
#        test.write(line)
#    test.close()
#
#    for iw in xrange(0,npts-1):
#        for iwp in xrange(0,npts-1):
#            EPS_C[iw]=EPS_C[iw]+XHI[iwp]*lorentzian(dE*float(iw-iwp),args.smear)
#        for iwp in xrange(-npts+1,-1):
#            EPS_C[iw]=EPS_C[iw]+np.conjugate(XHI[-iwp])*lorentzian(dE*float(-iw+iwp),args.smear)
#else:
#   EPS_C=XHI
 
EPS_C=1.+XHI

epsout=open("eps-contact_"+str(args.alpha)+".dat","w")
epsline=" Energy[eV]    Im[Eps]     Real[Eps] \n"
epsout.write(epsline)
for i in xrange(0,npts-1):
        epsline=" %.4g      %.4g        %.4g  \n" % (EPS[i,0],EPS_C[i].imag,EPS_C[i].real)
        epsout.write(epsline)
epsout.close()

