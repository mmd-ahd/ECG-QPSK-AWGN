def calculate_ber(original_bitstream, received_bitstream):

    if not original_bitstream: # Check for empty original bitstream
        return 0.0, 0, 0 
    
    len_orig = len(original_bitstream)
    len_recv = len(received_bitstream)
    
    errors = 0
    compare_len = min(len_orig, len_recv) # find shorter bitstream
    for i in range(compare_len):
        if original_bitstream[i] != received_bitstream[i]:
            errors += 1
            
    # Add lost bits as errors
    if len_recv < len_orig:
        errors += (len_orig - len_recv) # Count missing bits as errors
    
    ber_val = errors / len_orig # Calculate Bit Error Rate
    return ber_val, errors, len_orig
