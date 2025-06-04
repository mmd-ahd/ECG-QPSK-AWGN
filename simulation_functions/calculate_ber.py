def calculate_ber(original_bitstream, received_bitstream):
    """
    Calculates Bit Error Rate.
    Returns ber_value, number_of_errors, total_bits_in_original_stream.
    Adjusts error count if received bitstream is shorter than original.
    """
    if not original_bitstream: 
        return 0.0, 0, 0 
    
    len_orig = len(original_bitstream)
    len_recv = len(received_bitstream)
    
    errors = 0
    compare_len = min(len_orig, len_recv)
    for i in range(compare_len):
        if original_bitstream[i] != received_bitstream[i]:
            errors += 1
            
    if len_recv < len_orig:
        errors += (len_orig - len_recv) # Count missing bits as errors
    # If len_recv > len_orig, extra received bits are ignored for BER calculation against original length.
    
    if len_orig == 0: 
        return 0.0, errors, 0

    ber_val = errors / len_orig
    return ber_val, errors, len_orig