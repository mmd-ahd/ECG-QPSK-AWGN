import numpy as np
import wfdb

def get_ecg_segment_wfdb(path, channel, duration):

    signals, fields = wfdb.rdsamp(path) # Read the WFDB
    base_fs = fields['fs'] # Store the base sampling frequency

    # Check if channel is valid
    if not 0 <= channel < signals.shape[1]:
        err_msg = (f"Channel index {channel} is not valid for the signal "
                    f"'{path}'. Max index: {signals.shape[1]-1}.")
        return np.array([]), np.array([]), 0, err_msg

    ecg_full = signals[:, channel] # Extract the specified channel signal
    
    # Check if duration is valid
    max_duration_available = len(ecg_full) / base_fs
    if duration > max_duration_available:
        duration = max_duration_available

    num_samples_segment = int(duration * base_fs)
    if num_samples_segment == 0:
        err_msg = "Calculated samples for segment is zero."
        return np.array([]), np.array([]), 0, err_msg

    ecg_segment = ecg_full[:num_samples_segment] # Extract the segment
    time_vector_base = np.linspace(0, duration, num_samples_segment, endpoint=False) # Create time axis

    return ecg_segment, time_vector_base, base_fs, None
