import numpy as np

def quantize_signal(signal, num_bits):

    if len(signal) == 0:
        return "", np.array([]), 0.0, 0.0, 1.0 

    # find the range
    min_val = np.min(signal)
    max_val = np.max(signal)
    
    num_levels = 2**num_bits # Number of quantization levels
    step_size = (max_val - min_val) / num_levels # Calculate step size
    
    quantized_indices = np.round((signal - min_val) / step_size) # shift and scale to quantization levels then round
    quantized_indices = np.clip(quantized_indices, 0, num_levels - 1).astype(int) # Ensure indices are within bounds and convert to int
    quantized_values_for_plot = min_val + (quantized_indices + 0.5) * step_size # Calculate quantized values
    
    bitstream = ""
    for index in quantized_indices:
        bitstream += format(index, f'0{num_bits}b') # Convert index to binary string
        
    return bitstream, quantized_values_for_plot, min_val, max_val, step_size
