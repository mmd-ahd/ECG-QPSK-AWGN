import numpy as np
import scipy.signal

def resample_signal(signal, original_fs, target_fs, duration):

    if original_fs == target_fs: # No resampling needed
        if len(signal) == 0: # Check for empty signal
            return np.array([]), np.array([])
        return signal, np.linspace(0, duration, len(signal), endpoint=False)

    num_target_samples = int(duration * target_fs) # Calculate number of samples in target signal
    if num_target_samples <= 0:  
        return np.array([]), np.array([]) 
        
    try:
        if len(signal) == 0: # Check for empty signal
             return np.array([]), np.array([]) 
        resampled_signal = scipy.signal.resample(signal, num_target_samples) # Resample the signal
    except ValueError: 
        return np.array([]), np.array([]) # resampling failed

    time_vector_target = np.linspace(0, duration, num_target_samples, endpoint=False) # Create new time axis for target signal
    return resampled_signal, time_vector_target
