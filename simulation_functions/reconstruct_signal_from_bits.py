import numpy as np

def reconstruct_signal_from_bits(bitstream, num_bits, min_val, max_val, step_size):

    if not bitstream or num_bits <= 0: # Check for empty bitstream
        return np.array([])

    num_samples = len(bitstream) // num_bits # Calculate number of samples
    reconstructed_values = np.full(num_samples, np.nan)
    
    # Calculate the range of quantized values
    for i in range(num_samples):
        bits_for_sample_str = bitstream[i*num_bits : (i+1)*num_bits]
        # Check if we have enough bits for this sample
        if len(bits_for_sample_str) < num_bits: 

            continue 
        try:
            quantized_index = int(bits_for_sample_str, 2) # Convert bits to index
            reconstructed_values[i] = min_val + (quantized_index + 0.5) * step_size # Calculate the value
        except ValueError:
            continue # Remain NaN if conversion fails
        
    return reconstructed_values
