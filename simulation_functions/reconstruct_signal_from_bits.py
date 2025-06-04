import numpy as np

def reconstruct_signal_from_bits(bitstream, num_bits, min_val, max_val, step_size):
    """
    Reconstructs the signal from bits.
    Returns reconstructed_values_array. Puts np.nan for samples with conversion issues.
    """
    if not bitstream or num_bits <= 0: 
        return np.array([])

    num_samples = len(bitstream) // num_bits
    reconstructed_values = np.full(num_samples, np.nan) # Initialize with NaN
    
    for i in range(num_samples):
        bits_for_sample_str = bitstream[i*num_bits : (i+1)*num_bits]
        if len(bits_for_sample_str) < num_bits: 
            # This implies bitstream length was not a multiple of num_bits.
            # The loop range already ensures we don't go out of bounds.
            # This sample will remain NaN.
            continue 
        
        try:
            quantized_index = int(bits_for_sample_str, 2)
            reconstructed_values[i] = min_val + (quantized_index + 0.5) * step_size
        except ValueError:
            # Failed to convert bits to int, sample remains NaN
            continue
        
    return reconstructed_values