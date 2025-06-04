import numpy as np
import scipy.signal

def resample_signal(signal, original_fs, target_fs, duration_sec):
    """
    Resamples the signal to the target sampling rate.
    Returns resampled_signal, time_vector_target.
    Returns empty arrays if resampling is not possible or fails.
    """
    if original_fs == target_fs:
        if len(signal) == 0: # Handle empty input even if fs matches
            return np.array([]), np.array([])
        return signal, np.linspace(0, duration_sec, len(signal), endpoint=False)

    num_target_samples = int(duration_sec * target_fs)
    if num_target_samples <= 0: 
        return np.array([]), np.array([]) # Indicate failure for GUI to handle
        
    try:
        if len(signal) == 0:
             return np.array([]), np.array([]) # Cannot resample empty signal
        resampled_signal = scipy.signal.resample(signal, num_target_samples)
    except ValueError: # Catches issues from scipy.signal.resample
        return np.array([]), np.array([]) # Indicate failure

    time_vector_target = np.linspace(0, duration_sec, num_target_samples, endpoint=False)
    return resampled_signal, time_vector_target