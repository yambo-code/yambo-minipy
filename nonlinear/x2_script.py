#!/usr/bin/env python
import re
import argparse
import sys
import subprocess as sub
import pylab
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
parser.add_argument('-brng',    help='bands range',    type=int,   default=None,   dest="brange", nargs=2)
parser.add_argument('-frng',    help='frequency range',type=float, default=[0.5,10],   dest="frange", nargs=2)
parser.add_argument('-fstep',   help='frequency step', type=float, default="0.5",  dest="fstep")
parser.add_argument('-rtstep',  help='real-time step', type=float, default="0.005",dest="rtstep")
parser.add_argument('-nesteps', help='number of steps', type=int,   default=None,dest="nesteps")
parser.add_argument('-netime',  help='simulation time', type=float, default=None,dest="netime")
parser.add_argument('-edir',    help='Efield direction',type=float,   default=[1.0,0.0,0.0],dest="edir", nargs=3)
parser.add_argument('-eint',    help='Efield intensity',type=float,   default=1000,dest="eint")
parser.add_argument('-ypath',   help='yambo and ypp path',type=str,   default="",  dest="ypath")
parser.add_argument('-mpi',     help='mpi command',type=str,   default="",         dest="mpi")
parser.add_argument('-lf',      help='phase lifetime',type=float,   default=0.0,    dest="phlife")
parser.add_argument('-multi',   help='run multiple jobs', default=False,  dest="multi", action="store_true")

args = parser.parse_args()

print("\n\n ***  Second Haromic Generation with Yambo  ***\n")

if not args.netime and not args.nesteps:
    print(" Error set 'simulation time' or 'numer of steps' !! ")
    sys.exit(1)

frequencies = np.arange(args.frange[0],args.frange[1],args.fstep) 

print(" Frequencies :\n %s \n\n" % str(frequencies))
print(" Bands Range : %s " % str(args.brange))

b1=args.brange[0]
b2=args.brange[1]
rtstep =args.rtstep
if args.nesteps is None:
    nesteps=1
else:
    nesteps=args.nesteps

if args.netime is None:
    netime=0
else:
    netime=args.netime

edir1   =args.edir[0]
edir2   =args.edir[1]
edir3   =args.edir[2]
eint    =args.eint
phlife  =args.phlife

yambo=args.mpi+"  "+os.path.join(args.ypath,"yambo_rt")
yambo=yambo.strip()
ypp  =os.path.join(args.ypath,"ypp_rt")
ypp=ypp.strip()

print(" Yambo : %s " % str(yambo))
print(" Ypp   : %s " % str(ypp))

f = open('ypp.in_x2','w')                                                                    
f.write("""
rtX                          # [R] Real-Time Response functions Post-Processing
Xorder= 4                    # Max order of the response functions
ProbeKey= "freq"             # Keyword to select groups of PROBE databases
PumpKey= "none"              # Keyword to select groups of PUMP databases
% EnRngeRt
 0    | 20    | eV    # Energy range
%
ETStpsRt= 200                # Total Energy steps
PrtErr                      # Print error (default=no)
% TmRngeRt
  -1.000000 | -1.00000 | fs    # Time-window where processing is done
%
DampMode= "LORENTZIAN"             # Damping type ( NONE | LORENTZIAN | GAUSSIAN )
DampFactor=  0.1   eV    # Damping parameter
TDResponse= "pol"            # Time-dependet response (pol | cur | Bpol | Bcur )
""")
f.close()

ybproc=[]

print(" \n\n Staring Calculation\n\n")
for freq in frequencies:
    print(" Doing %f .... " % freq)
    outdir="freq%g_ " % (freq)
    outdir=outdir.strip()
    if(os.path.exists(outdir)):
        print(" Warning directory %s already exist !" % outdir)
        shutil.rmtree(outdir)
    f = open('yambo.in_%f' % freq,'w')                                                                    
    f.write("""
negf                         # [R] Real-Time dynamics
scpot                        # [R] Self-Consistent potentials
Potential= "default"         # [SC] SC Potential
%%SCBands
 %(b1)d | %(b2)d |                   # [SC] Bands
%%
BandMix= 100.0000            # [SC] Band mixing
CollPath= ""                 # [SC,RT] Path to the collisions databases
Integrator= "RK2"         # [RT] Integrator (RK2 | EULER | EXACT | RK2EXACT)
DynKind= "P"                 # [RT] Dynamics kind ((C)arriers/(P)olarization)
QPLifeTime= 0.000000   fs         # [RT] QP Relaxation Time
PhLifeTime= %(phlife)g fs         # [RT] Phase Relaxation Time
RTstep = %(rtstep)g    fs         # [RT] Real Time step length
NEsteps= %(nesteps)d              # [RT] Non-equilibrium Time steps
NETime= %(netime)g          fs    # [RT] Non-equilibrium  max Time
RTfreezeH                   # [RT] Hartree not updated during RT
RTfreezeXC                  # [RT] XC potential/self-energy not updated during RT
%% Probe_Freq
  %(freq)g | %(freq)g | eV    # [RT Probe] Frequency
%%
Probe_FrStep= 0.000000 eV    # [RT Probe] Frequency step
Probe_Int= %(eint)g    kWLm2 # [RT Probe] Intensity
Probe_kind= "SIN"           # [RT Probe] Kind(SIN|RES|ANTIRES|GAUSS|DELTA|QSSIN)
%% Probe_Dir
  %(edir1)g | %(edir2)g | %(edir3)g |        # [RT Probe] Versor
%%
#RTtdse                      # [RT] Use Time-dependent Schrodinger Equation
#RTDynBerry                  # [RT] Use Dynamic Berry Phase
#RTFixOverlap                # [RT] Fix valence bands overlaps to the identity
#RTOvrlpLim                  # [RT] Use exact limit for interblock bands in the S matrix
#RTDipCov                    # [RT] Use covariant dipole formulation

""" % vars())
    f.close()
    cmd=yambo+" -F yambo.in_%f -S -J %s -C %s " % (freq,outdir,outdir)
    print(" Comand : %s " % str(cmd))

    try:
        yb=sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True)
        ybproc.append(yb)
        if not args.multi:
            yb.wait()
    except:
        output, errors = yb.communicate()
        print(" Error:  %s  " % str(errors))
        print(" Output: %s  " % str(output))

if args.multi:
    for yb in ybproc:
        yb.wait()

cmd=ypp+" -F ypp.in_x2 -N"
yp = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE,shell=True)
output, errors = yp.communicate()

