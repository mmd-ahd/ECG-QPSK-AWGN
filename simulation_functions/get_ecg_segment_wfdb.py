import numpy as np
import wfdb

def get_ecg_segment_wfdb(record_path_name, channel_index, duration_sec):
    """
    Loads an ECG signal segment from a WFDB record.
    Returns: ecg_segment, time_vector_base, base_fs, error_message (None if no error)
    """
    try:
        signals, fields = wfdb.rdsamp(record_path_name)
        
        base_fs = fields['fs']
        # signal_names = fields['sig_name'] # Not strictly needed if not reported

        if not 0 <= channel_index < signals.shape[1]:
            err_msg = (f"Channel index {channel_index} out of bounds for record "
                       f"'{record_path_name}'. Max index: {signals.shape[1]-1}.")
            return np.array([]), np.array([]), 0, err_msg

        ecg_full = signals[:, channel_index]
        # selected_channel_name = signal_names[channel_index]
        
        max_duration_available = len(ecg_full) / base_fs
        if duration_sec > max_duration_available:
            # Adjust duration if requested is too long, GUI can be notified via status if needed
            duration_sec = max_duration_available
        
        num_samples_segment = int(duration_sec * base_fs)
        if num_samples_segment == 0:
             err_msg = "Calculated samples for segment is zero. Check duration or record length."
             return np.array([]), np.array([]), 0, err_msg

        ecg_segment = ecg_full[:num_samples_segment]
        time_vector_base = np.linspace(0, duration_sec, num_samples_segment, endpoint=False)
        
        return ecg_segment, time_vector_base, base_fs, None # No error

    except FileNotFoundError:
        err_msg = (f"WFDB record '{record_path_name}' (.hea or .dat) not found. Check path.")
        return np.array([]), np.array([]), 0, err_msg
    except wfdb.io.record.RecordNotFoundError: 
        err_msg = (f"WFDB record '{record_path_name}' not found by wfdb library.")
        return np.array([]), np.array([]), 0, err_msg
    except Exception as e:
        err_msg = f"Loading WFDB record '{record_path_name}' failed: {type(e).__name__}."
        return np.array([]), np.array([]), 0, err_msg