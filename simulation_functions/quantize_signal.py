import numpy as np

def quantize_signal(signal, num_bits):
    """
    Quantizes the signal.
    Returns bitstream, quantized_values_for_plot, min_val, max_val, step_size.
    """
    if len(signal) == 0:
        return "", np.array([]), 0.0, 0.0, 1.0 

    min_val = np.min(signal)
    max_val = np.max(signal)
    
    if min_val == max_val: 
        max_val = min_val + 1e-9 
        if min_val == max_val: 
            max_val = min_val + np.finfo(float).eps 

    num_levels = 2**num_bits
    step_size = (max_val - min_val) / num_levels
    
    if step_size == 0: 
        step_size = 1e-9 

    quantized_indices = np.round((signal - min_val) / step_size) 
    quantized_indices = np.clip(quantized_indices, 0, num_levels - 1).astype(int)
    quantized_values_for_plot = min_val + (quantized_indices + 0.5) * step_size
    
    bitstream = ""
    for index in quantized_indices:
        bitstream += format(index, f'0{num_bits}b') 
        
    return bitstream, quantized_values_for_plot, min_val, max_val, step_size