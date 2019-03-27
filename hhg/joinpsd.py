#! /usr/bin/python
"""      AUTHOR: Myrta Gruening
         CREATED: 27/10/2011
         LAST MODIFIED: 6/11/2011"""
import sys,argparse,glob
#
# Bug in aiken (comment on other machines)
#
#sys.path.remove('/usr/share/pyshared')
#
from scipy import *
from scipy import interpolate
from pylab import *
from matplotlib.colors import LogNorm
from spectrum import *
#
# parameters/dictionaries 
#
h = 4.135667516
pi = 3.14159265
speed_light = 2.99792458e+8
vacuum_perm = 1e+7/4./pi/speed_light**2
TOL = 1.e-4
IF_title_label={False:"Laser Intensity",True:"Laser Field"}
IF_unit_label={False:"kW/cm^2",True:"V/m"}
LongProgramName = 'JoinPSD: JoinPowerSpectralDensities'
LastModified = 'Last modified: 06/11/2011'
#
# def function
#
def read_psd(A):
    f =[]
    p =[]
    istring=A.readline()
    while istring.endswith('\n'):
        if not istring.startswith('#'):
            tbl=istring.split()
            f.append(float(tbl[0]))
            p.append(float(tbl[1]))
        istring=A.readline()
        if istring.startswith('#'):
            if istring.find('Probe_Int')!=-1:
                l = istring.index('=')
                u = istring.index('kWLm2')
                info = float(istring[l+1:u])
    return info,array(f),array(p)
#
def normalize_spectrum(s):
    s = s/max(s)
    return 
def detect_harmonic(oddeven,f,a,max_harm,tol):
    what={"odd":[2,2],"even":[1,2],"all":[0,1]}
    indx_harm = array([]) 
    for ii in range(what[oddeven][0],max_harm,what[oddeven][1]):
        indx_harm = append(indx_harm,argwhere(abs(f-(ii+1)*a)<tol)) # Here I find the index of f for which f is a harmonic of a
    return list(indx_harm) #return the list of indexes
def omega(E):
    return h/(2*pi*E)
def Intensity2Field(I):
    CF=1e+7/speed_light/vacuum_perm #NB using definition in Yambo... (really miss a .5)
    return sqrt(I*CF)
#
#
#
if __name__ == "__main__":
#
# parse command line
#
    parser = argparse.ArgumentParser(prog='joinpsd',description='Read in several power spectra from y2psd and analyze the results',epilog="Copyright Myrta Gruning 2011")
    parser.add_argument('suffix', help='suffix power spectrum files',type=str)
    parser.add_argument('-m','--maxfreq', help='maximum frequence for plot, in eV',nargs='?',type=float,default=0.0)
    parser.add_argument('-a','--harmonic', help='harmonic frequence for plot, in eV',nargs='?',type=float,default=0.0)
    parser.add_argument('-p','--plot', help='type of plot',nargs='?',type=str,default='simple',choices=['simple', 'pcolor','harmonics','analysis'])
    parser.add_argument('-n','--normalize', help='normalized each spectra to its maximum',action='store_true')
    parser.add_argument('-l','--logscale', help='use logaritmic scale for y axis in pcolor plot',action='store_true')
    parser.add_argument('-w','--which', help='all/even/odd harmonics for harmonics plot',type=str,default='odd',nargs='?',choices=["odd","even","all"])
    parser.add_argument('-c','--cutoff', help='intensity cutoff for ',type=float,default=1.e-4,nargs='?')
    parser.add_argument('-f','--field', help='use laser field instead of laser intensity in analysis',action='store_true')
    parser.add_argument('-g','--gap', help='band gap of the material',type=float,nargs='?',default=0.0)
    parser.add_argument('-i','--intensity', help='output ratiated intensity instead of power-spectrum',action='store_true')
    parser.add_argument('-C','--cmap', help='color map for pcolor plot',type=str,default='jet',nargs='?',choices=["autumn", "bone", "cool", "copper", "flag", "gray", "hot", "hsv", "jet", "pink", "prism", "spring", "summer", "winter"])
    args = parser.parse_args()
#
# report parameters
#
    print LongProgramName
    print LastModified+'\n'
    path = "."
    expr = '*'+args.suffix+'*'
    Y_ = array([])
    list_psd = []
    for infile in glob.glob(os.path.join(path,expr)):
        inf = open(infile,'r') 
        print " Reading power spectrum from file {0:}".format(infile)
        laser_intensity, X_, p = read_psd(inf)
        if (args.field):
                    Y_ = append(Y_,Intensity2Field(laser_intensity))
        else:
                    Y_ = append(Y_,laser_intensity)
        whatisp = "Power spectrum"
        if (args.intensity):
            print "   Power spectrum converted to radiated intensity"
            for ii in range(1,len(X_)):
                Omegafourth = omega(X_[ii])**4
                p[ii] = p[ii]*Omegafourth
            whatisp = "Radiated intensity"
        if args.normalize:
            print "   Normalizing spectrum"
            list_psd.append(normalize_spectrum(p))
        else:
            list_psd.append(p)
        print "   Laser intensity {0:.2e}".format(laser_intensity)
        #
    f_max = X_[len(X_)-1]
    Fac = 1.
    whatisx = 'Freq (eV)'
    if args.maxfreq > 0:
        f_max = args.maxfreq
    indx_max = int(f_max/X_[1])
    harm_freq = args.harmonic
    Z_ = array(list_psd)
    sorted_indx = Y_.argsort()
    Y = Y_[sorted_indx]
    X = X_[0:indx_max]
    Z = Z_[sorted_indx,0:indx_max]
    if (harm_freq != 0):
        Fac = harm_freq
        whatisx = 'Harmonic order'
    #
    if args.plot == 'simple':
        a = subplot(len(Y),1,1)
        semilogy(X/Fac,Z[0],label="{0:.1e} {1:}".format(Y[0],IF_unit_label[args.field]))
        legend()
        ylim(min(Z[0]),max(Z[0]))
        title(whatisp +"(arb. units)") 
        for i in range(1,len(Y)):
             subplot(len(Y),1,i+1,sharex=a,sharey=a)
             semilogy(X/Fac,Z[i],label="{0:.1e} {1:}".format(Y[i],IF_unit_label[args.field]))
             legend()
             ylim(min(Z[i]),max(Z[i]))
        xlabel(whatisx)
        xlim(0,f_max/Fac)
    elif args.plot == 'pcolor':
	if args.logscale:
        	y = 10**linspace(log10(Y[0]),log10(max(Y)),len(Y))
	else:
        	y = arange(0,max(Y)+Y[0],Y[0])
        pcolor(X/Fac,y,Z,norm=LogNorm(vmin=Z.min(), vmax=Z.max()),cmap=args.cmap)
        xlabel(whatisx)
        xlim(0,f_max/Fac)
        ylabel(IF_title_label[args.field]+" ("+IF_unit_label[args.field]+")")
        cb = colorbar()
    	cb.set_label(whatisp)
    elif (args.plot == 'harmonics') or (args.plot == 'analysis'):
        # If harmonic freq not defined find it
        ind_hf = argmax(Z[0])
        if (harm_freq == 0):
            harm_freq = X[ind_hf]
            print "Main frequency determined from maximum of psd {0:} eV".format(harm_freq) 
        indx_harmonics = detect_harmonic(args.which,X,harm_freq,int(f_max/harm_freq),TOL)
        figure(1)
        a = subplot(len(Y),1,1)
        k = zeros(len(indx_harmonics))
        k[:] = min(Z[0,indx_harmonics])
        vlines(indx_harmonics/ind_hf,log10(k),log10(Z[0,indx_harmonics]),label="{0:.1e} {1:}".format(Y[0],IF_unit_label[args.field]))
        legend()
        title("Log_10(" +whatisp+ ")(arb. units)") 
        for i in range(1,len(Y)):
            subplot(len(Y),1,i+1,sharex=a)
            vlines(indx_harmonics/ind_hf,log10(k),log10(Z[i,indx_harmonics]),label="{0:.1e} {1:}".format(Y[i],IF_unit_label[args.field]))
            legend()
        xlabel("Harmonic order")
        ylim(log10(min(Z[0,indx_harmonics])),log10(max(Z[0,indx_harmonics])))
        if (args.plot == 'analysis'):
            figure(2)
            F_cutoff = array([])
            for i in range(len(Y)):
                indx_cutoff = argwhere(Z[i,indx_harmonics]<args.cutoff)[0]
                F_cutoff = append(F_cutoff,int((indx_harmonics[indx_cutoff])/ind_hf-2))
            plot(Y,F_cutoff,'o-')
            xlabel(IF_title_label[args.field]+" ("+IF_unit_label[args.field]+")")
            ylabel("Frequency cutoff (Harmonic order)")
            figure(3)
            max_cutoff = int(F_cutoff[-1])
            if args.gap == 0:
                min_h = 7
            else:
                min_h = int(args.gap/harm_freq)
            for i in range(min_h,max_cutoff,2):
                loglog(Y,Z[:,i*ind_hf],'o-',label=str(i))
            xlabel(IF_title_label[args.field]+" ("+IF_unit_label[args.field]+")")
            ylabel("PSD Intensity (arb. units)")
            legend()
	#
    show()
