def peakdetect(y_axis, x_axis = None, lookahead = 500, delta = 0): #copied from https://gist.github.com/1178136 nad modified
    maxval = []
    maxpos = []
#    mintab = []
    dump = [] #Used to pop the first hit which always if false
    length = len(y_axis)
    if x_axis is None:
        x_axis = range(length)
    #perform some checks
    if length != len(x_axis):
        raise ValueError, "Input vectors y_axis and x_axis must have same length"
    if lookahead < 1:
        raise ValueError, "Lookahead must be above '1' in value"
    if not (np.isscalar(delta) and delta >= 0):
        raise ValueError, "delta must be a positive number"    
    #needs to be a numpy array
    y_axis = asarray(y_axis)
    #maxima and minima candidates are temporarily stored in
    #mx and mn respectively
    mx = Inf
    #Only detect peak if there is 'lookahead' amount of points after it
    for index, (x, y) in enumerate(zip(x_axis[:-lookahead], y_axis[:-lookahead])):
        if y > mx:
            mx = y
            mxpos = x
        ####look for max####
        if y < mx-delta and mx != Inf:
            #Maxima peak candidate found
            #look ahead in signal to ensure that this is a peak and not jitter
            if y_axis[index:index+lookahead].max() < mx:
                maxpos.append(mxpos)
                maxval.append(mx)
                dump.append(True)
                #set algorithm to only find maxima now
                mn = -Inf
                mx = -Inf
    #Remove the false hit on the first value of the y_axis
    try:
        if dump[0]:
            maxtab.pop(0)
            #print "pop max"
        del dump
    except IndexError:
        #no peaks were found, should the function return empty lists?
        pass
    return asarray(maxpos),asarray(maxval)
#
def peakdetect_zero_crossing(y_axis, x_axis = None, window = 49): #copied from https://gist.github.com/1178136
    if x_axis is None:
        x_axis = range(len(y_axis))
    
    length = len(y_axis)
    if length != len(x_axis):
        raise ValueError, 'Input vectors y_axis and x_axis must have same length'
    
    #needs to be a numpy array
    y_axis = asarray(y_axis)
    
    zero_indices = zero_crossings(y_axis, window = window)
    period_lengths = diff(zero_indices)
    
    bins = [y_axis[indice:indice+diff] for indice, diff in
        zip(zero_indices, period_lengths)]
    
    even_bins = bins[::2]
    odd_bins = bins[1::2]
    #check if even bin contains maxima
    if even_bins[0].max() > abs(even_bins[0].min()):
        hi_peaks = [bin.max() for bin in even_bins]
        lo_peaks = [bin.min() for bin in odd_bins]
    else:
        hi_peaks = [bin.max() for bin in odd_bins]
        lo_peaks = [bin.min() for bin in even_bins]
    
    
    hi_peaks_x = [x_axis[where(y_axis==peak)[0]] for peak in hi_peaks]
    lo_peaks_x = [x_axis[where(y_axis==peak)[0]] for peak in lo_peaks]
    
    maxtab = [(x,y) for x,y in zip(hi_peaks, hi_peaks_x)]
    mintab = [(x,y) for x,y in zip(lo_peaks, lo_peaks_x)]
    
    return maxtab, mintab
