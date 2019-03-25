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
parser = argparse.ArgumentParser(prog='x2script',description='Second Harmonic Generation script',epilog="Copyright Claudio Attaccalite 2013")
parser.add_argument('-np', help='Number of preocessors', type=int,   default=1,dest="nproc")

args = parser.parse_args()

print("\n\n ***  Second Haromic Generation with Yambo  ***\n")

freq_steps=30
min_freq=2.00
max_freq=8.00
yambo="/home/attacc/bin/yambo_rt -N"

print(" Number of processors  : %d " % args.nproc)
print(" Number of Frequencies : %d " % freq_steps)
print(" Frequency Range       : %f eV - %f eV " % (min_freq,max_freq))

if args.nproc <= freq_steps:
    n_freq_group =freq_steps/args.nproc
    n_proc_group =1
    n_groups     =args.nproc
else:
    n_freq_group =freq_steps
    n_proc_group =int(float(args.nproc)/freq_steps)
    n_groups     =freq_steps

print(" Number of groups                 : %d " % n_groups) 
print(" Number of frequencies per group  : %d " % n_freq_group) 
print(" Number of processors  per group  : %d " % n_proc_group)

# 
# Now makes the groups
# 

groups=[]

for ig in xrange(0,n_groups):
    glist=[]
    for ifreq in xrange(0,freq_steps):
        if ifreq%n_groups == ig:
            glist.append(ifreq)
    groups.append(glist)

for group in enumerate(groups):
    print(" Group %d : %s " % (group[0],str(group[1])))

print("\n\n Starting Calculations.... \n\n")


for group in enumerate(groups):
    print(" Doing group  : %d ...... " % group[0])
    ybgroup=[]
    for freq in group[1]:
        outdir="SN%d" % freq
        f=open('yambo.in_%d' % freq,'w')
        f.write("""
negf                         # [R] Real-Time dynamics
scpot                        # [R] Self-Consistent potentials
Potential= "default"         # [SC] SC Potential
%% SCBands
  1 | 16 |                   # [SC] Bands
%%
BandMix= 100.0000            # [SC] Band mixing
CollPath= ""                 # [SC,RT] Path to the collisions databases
Integrator= "INVINT"            # [RT] Integrator (RK2 | EULER | EXACT | RK2EXACT)
QPLifeTime= 6.000000   fs    # [RT] QP Relaxation Time
PhLifeTime= 6.000000   fs    # [RT] Phase Relaxation Time
RTstep=   0.00500       fs    # [RT] Real Time step length
NEsteps= 1                   # [RT] Non-equilibrium Time steps
NETime= 55.000000       fs    # [RT] Non-equilibrium  max Time (alternative to NEsteps)
IOtime= 5.000000       fs    # [RT] Time between to consecutive I/O
RTfreezeH                   # [RT] Hartree not updated during RT
RTfreezeXC                  # [RT] XC potential/self-energy not updated during RT
%% Probe_Freq
 %(freq)g | %(freq)g  | eV    # [RT Probe] Frequency
%%
Probe_FrStep= 0.000000 eV    # [RT Probe] Frequency step
Probe_Int= 1.000000    kWLm2 # [RT Probe] Intensity
Probe_kind= "SIN"           # [RT Probe] Kind(SIN|RES|ANTIRES|GAUSS|DELTA|QSSIN)
%% Probe_Dir
 1.000000 | 0.000000 | 0.000000 |        # [RT Probe] Versor
%%
RTtdse                       # [RT] Use Time-dependent Schrodinger Equation
RTDynBerry                   # [RT] Use Dynamic Berry Phase
RTDipCov                     # [RT] Use covariant dipole formulation
""" % vars())
        f.close()
        cmd=yambo+" -F yambo.in_%d -M -S -J %s -C %s " % (freq,outdir,outdir)
        print(" Comand : %s " % str(cmd))
#        try:
#            yb=sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True)
#            ybgroup.append(yb)
#        except:
#            output, errors = yb.communicate()
#            print(" Error:  %s  " % str(errors))
#            print(" Output: %s  " % str(output))
#
#   Wait that the group finished
#
#    for yb in ybgroup:
#        yb.wait()



