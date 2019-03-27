#! /usr/bin/python
"""      AUTHOR: Myrta Gruening
         CREATED: 18/10/2011
         LAST MODIFIED: 31/10/2011"""
import sys,argparse
#
# Bug in aiken (comment on other machines)
#
#sys.path.remove('/usr/share/pyshared')
#
import numpy as np
import re
from scipy import *
from scipy import interpolate
from pylab import *
from spectrum import *
#
# parameters/dictionaries 
#
h = 4.135667516
pi = 3.14159265
LongProgramName = 'Y2PSD: Yambo2PowerSpectralDensity'
LastModified = 'Last modified: 31/10/2011'
XYZ = {'x':1,'y':2,'z':3}    
#
# def function
#
def read_polarization(pfile,direction):
    data=np.genfromtxt(pfile,comments="#")
    t_=data[:,0]
    p_=data[:,direction]
    pfile.seek(0)
    plines=pfile.read()
    pattern=r'\s*Frequency\svalue\s*(\d*)'
    match = re.search(pattern, plines, re.MULTILINE)
    freq = float(match.group(1))
    info = "Laser frequency "+match.group(1)
    return t_,p_,info

def write_psd(A,f,p,info,lim):
    s = '#\n#'+ LongProgramName+'\n#'+LastModified+'\n#\n' 
    s = s + '# Freq(eV) \t PSD(arb.unit) \n'
    indx = int(lim/f[1])
    for i in range(indx): #read only positive freq part
        A.write(s)
        s = str(f[i])+'\t'+str(p[i])+'\n'
    A.write(info)
    return 
def Nyquist_freq(time_interval):
    return 1./time_interval/2.
def normalize_spectrum(s):
    s = s/max(s)
    return s
#
#
#
if __name__ == "__main__":
#
# parse command line
#
    parser = argparse.ArgumentParser(prog='y2psd',description='Read in input polarization from yambo_rt and output the power spectrum',epilog="Copyright Myrta Gruning 2011")
    parser.add_argument('infile', help='input polarization file',type=argparse.FileType('r'))
    parser.add_argument('outfile', help='output the file with PSD (optional)', nargs='?', type=argparse.FileType('w'))
    parser.add_argument('-s','--suppress', help='suppress graphical output (no arg)',action='store_true')
    parser.add_argument('-i','--initime', help='initial time, in fs',nargs='?',type=float,default=0.0)
    parser.add_argument('-d','--direction', help='direction, x,y,z',nargs='?',type=str,default='x',choices=['x','y','z'])
    parser.add_argument('-e','--endtime', help='final time, in fs',nargs='?',type=float,default=10000.0)
    parser.add_argument('-m','--maxfreq', help='maximum frequence for plot, in eV',nargs='?',type=float,default=0.0)
    parser.add_argument('-a','--harmonic', help='harmonic frequence for plot, in eV',nargs='?',type=float,default=0.0)
    parser.add_argument('-w','--window', help='window for FFT',nargs='?',default='hamming',type=str,choices=['tukey', 'gaussian', 'riesz', 'hanning', 'lanczos', 'rectangular', 'chebwin', 'bohman', 'kaiser', 'blackman_harris', 'cosine', 'blackman', 'rectangle', 'hann', 'triangular', 'nuttall', 'bartlett', 'poisson_hanning', 'sine', 'sinc', 'parzen', 'riemann', 'blackman_nuttall', 'cauchy', 'flattop', 'bartlett_hann', 'poisson', 'hamming'])
    parser.add_argument('-n','--neighbors', help='number of neighbors for filtering',nargs='?',default=2,type=int)
    parser.add_argument('-p','--power', help='minimum power',nargs='?',default=10e-9,type=float)
    parser.add_argument('-x','--derive', help='Use first or second derivative of polarization',nargs='?',default=0,type=int,choices=[0,1,2])
    args = parser.parse_args()
#
#
# report parameters
#
    print LongProgramName
    print LastModified+'\n'
    print "Reading polarization in direction {0:} from file {1:}".format(args.direction,args.infile.name)
    write_to_file = False
    harm_freq = args.harmonic
    if args.outfile != None:
        print "Power spectrum written on file {0:}".format(args.outfile.name)
        write_to_file = True
    direction = XYZ[args.direction]
    t_,P_,info=read_polarization(args.infile,direction)
    dt = t_[1]
    if args.derive > 0:
        for n in range(args.derive):
            P_=gradient(P_)
            P_ = P_/dt
    t_i = args.initime
    t_f = min(args.endtime,t_[len(t_)-1])
    if (harm_freq != 0):
        Period = h/harm_freq
        n = int((t_f-t_i)/Period)
        t_f = t_i + (n-1)*Period
    n_i = int(t_i/dt)
    n_f = int(t_f/dt)
    P = P_[n_i:n_f]
    t = t_[n_i:n_f]
    no_plot = args.suppress
    lim_freq = Nyquist_freq(dt)
    if (args.maxfreq!=0.0):
        lim_freq = args.maxfreq
    window_type = args.window
    NP = args.neighbors
    print "Time interval {0:}-{1:} fs".format(t_i,t_f)
    print "Time step: {0:} fs".format(dt)
    print "Number of Steps: {0:}".format(len(t))
    print "Type of window for DFT: {0:}".format(window_type)
    print "Number of Neighbors in Daniell filtering: {0:}\n".format(NP)
    print "Yambo input file:\n{0:}".format(info) 
#
# compute periodogram and plot
#
    if NP != 0:
        p,f = DaniellPeriodogram(P,NP,NFFT=len(P),window=window_type)
    else:
        p = speriodogram(P,NFFT=len(P),window=window_type)
    f=array(fftfreq(p.size,dt))
    if write_to_file:
	psd_info =  '# Type of window for DFT: ' + str(window_type) + '\n'
	psd_info += '# Number of Neighbors in Daniell filtering:'+ str(NP) + '\n'
	psd_info += '# Yambo input:\n' + info 
        write_psd(args.outfile,h*f/2,p,psd_info,lim_freq)
#
# draw plot 
#
    subplot(211)
    plot(t,P,'m-')
    ylabel('Polarization')
    xlabel('Time (fs)')
    subplot(212)
    Fac = 1.
    whatisx = 'Freq (eV)'
    if (harm_freq != 0):
        Fac = harm_freq
        whatisx = 'Harmonic order'
    semilogy(h*f/2/Fac,normalize_spectrum(p),'m-')
    xlim(0,lim_freq/Fac)
    ylim(args.power,1)
    xlabel(whatisx)
    ylabel('Power Spectrum (arb. units)')
    if not no_plot:
        show()
    else:
        print 'Graphical output suppressed'
"""
Changelog:

25/10/2011: added direction option
	    implemented write to output  
	    reading and reporting yambo input
27/10/2011: added minimum power option
            added more info on output
            added interpolation (though it does not help!)
31/10/2011: added velocity/acceleration of dipole (not working)
            eliminated interpolation option 
            # if args.interpolate !=0:
            #     lim_indx = int(lim_freq/f[1])
            #     interp = interpolate.UnivariateSpline(f[:lim_indx+1],p[:lim_indx+1],k=5,s=0)
            #     Df = harm_freq/args.interpolate
            #     f_new = arange(0,lim_indx*f[1],Df)
            #     p_int = interp(f_new)
            #     semilogy(h*f_new/2/Fac,normalize_spectrum(p_int),'b--',label='interpolated')
"""
