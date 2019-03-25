#!/usr/bin/env python
import re
import argparse
import sys
import subprocess as sub
import os as os
import numpy as np
import shutil

"""
Second Harminc Generation script
"""
#
# parse command line
#
parser = argparse.ArgumentParser(prog='x2angle',description='Second Harmonic Generation script',epilog="Copyright Claudio Attaccalite 2013")

args = parser.parse_args()

print("\n\n ***  Second Haromic Generation with Yambo  ***\n")

freq=1.531
nangle=36
yambo="/home/attacc/bin/yambo_rt"

print(" Number of Frequencies : %d " % nangle)
print(" Frequency             : %f eV " % (freq))

for angle in xrange(0,nangle/2):
    rad=2.*np.pi*float(angle)/float(nangle)
    print("Radiant : %f " % rad)
    x1=np.cos(rad)
    y1=np.cos(rad)

    print(" Doing group  : %d ...... " % angle)
    outdir="SN%d_" % angle
    f=open('yambo.in_%d' % angle,'w')
    f.write("""
negf                         # [R] Real-Time dynamics
scpot                        # [R] Self-Consistent potentials
Potential= "default"         # [SC] SC Potential
%% SCBands
  1 | 8 |                   # [SC] Bands
%%
BandMix= 100.0000            # [SC] Band mixing
CollPath= ""                 # [SC,RT] Path to the collisions databases
Integrator= "INVINT"            # [RT] Integrator (RK2 | EULER | EXACT | RK2EXACT)
QPLifeTime= 6.000000   fs    # [RT] QP Relaxation Time
PhLifeTime= 6.000000   fs    # [RT] Phase Relaxation Time
RTstep=   0.002500       fs    # [RT] Real Time step length
NEsteps= 1                   # [RT] Non-equilibrium Time steps
NETime= 60.000000       fs    # [RT] Non-equilibrium  max Time (alternative to NEsteps)
IOtime= 5.000000       fs    # [RT] Time between to consecutive I/O
RTfreezeH                   # [RT] Hartree not updated during RT
RTfreezeXC                  # [RT] XC potential/self-energy not updated during RT
%% Probe_Freq
 %(freq)g | %(freq)g  | eV    # [RT Probe] Frequency
%%
Probe_FrStep= 0.000000 eV    # [RT Probe] Frequency step
Probe_Int= 100.000000    kWLm2 # [RT Probe] Intensity
Probe_kind= "SIN"           # [RT Probe] Kind(SIN|RES|ANTIRES|GAUSS|DELTA|QSSIN)
%% Probe_Dir
 %(x1)g | %(y1)g | 0.000000 |        # [RT Probe] Versor
%%
RTtdse                       # [RT] Use Time-dependent Schrodinger Equation
RTDynBerry                   # [RT] Use Dynamic Berry Phase
RTDipCov                     # [RT] Use covariant dipole formulation
""" % vars())
    f.close()
    args=" -F yambo.in_%d -M -N -S -J %s -C %s " % (angle,outdir,outdir)
    try:
        sub.call(yambo + args,shell=True)
    except:
         print(" Error doing : %s " % str(yambo+args))
