import numpy as np
import scipy.fft

def estimate_bandwidth(signal, fs, percentile=0.99):

    if len(signal) == 0: # Check for empty signal
        return 0.0 
    N = len(signal) # Number of samples
    yf = scipy.fft.fft(signal) # Compute the FFT
    xf = scipy.fft.fftfreq(N, 1 / fs) # Frequencies
    
    positive_freq = np.where(xf >= 0)
    xf_pos = xf[positive_freq]
    power_spec = (np.abs(yf[positive_freq])**2) # Power spectrum

    if len(power_spec) == 0 or np.sum(power_spec) == 0:  # if power spectrum is empty or zero return half the sampling frequency
        return float(fs / 2.0) 

    cumulative_power = np.cumsum(power_spec) # Cumulative power spectrum
    total_power = cumulative_power[-1] # store total power by last element
    
    if total_power == 0: # if total power is zero, return half the sampling frequency
         return float(fs / 2.0)

    try:
        bw_index = np.where(cumulative_power >= percentile * total_power)[0][0] # Find the index of the bandwidth
        bandwidth = xf_pos[bw_index]
    except IndexError:
        bandwidth = xf_pos[-1] if len(xf_pos) > 0 else float(fs / 2.0)

    return float(bandwidth)
