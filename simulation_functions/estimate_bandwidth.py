import numpy as np
import scipy.fft

def estimate_bandwidth(signal, fs, percentile=0.99):
    """
    Estimates the bandwidth of a signal using FFT.
    Returns the estimated bandwidth in Hz.
    """
    if len(signal) == 0:
        return 0.0 
    N = len(signal)
    yf = scipy.fft.fft(signal)
    xf = scipy.fft.fftfreq(N, 1 / fs)
    
    positive_freq_indices = np.where(xf >= 0)
    xf_pos = xf[positive_freq_indices]
    yf_pos_mag_sq = (np.abs(yf[positive_freq_indices])**2) 

    if len(yf_pos_mag_sq) == 0 or np.sum(yf_pos_mag_sq) == 0:
        return float(fs / 2.0)

    cumulative_power = np.cumsum(yf_pos_mag_sq)
    total_power = cumulative_power[-1]
    
    if total_power == 0: 
         return float(fs / 2.0)

    try:
        bw_index = np.where(cumulative_power >= percentile * total_power)[0][0]
        bandwidth = xf_pos[bw_index]
    except IndexError:
        bandwidth = xf_pos[-1] if len(xf_pos) > 0 else float(fs / 2.0)

    return float(bandwidth)