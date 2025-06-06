import numpy as np

def qpsk_modulate(bitstream):

    processed_bitstream = bitstream
    if len(processed_bitstream) % 2 != 0: # Check if the length is odd
        processed_bitstream = processed_bitstream[:-1] # chop off the last bit

    symbols = []
    # QPSK mapping
    mapping = {
        '00': (1 + 1j) / np.sqrt(2), # Positive in-phase and positive quadrature
        '01': (-1 + 1j) / np.sqrt(2), # Negative in-phase and positive quadrature
        '10': (-1 - 1j) / np.sqrt(2), # Negative in-phase and negative quadrature
        '11': (1 - 1j) / np.sqrt(2)  # Positive in-phase and negative quadrature
    }
    # Process the bitstream in dibits
    for i in range(0, len(processed_bitstream), 2):
        dibit = processed_bitstream[i:i+2]
        if len(dibit) == 2: 
             symbols.append(mapping[dibit]) # Map dibit to QPSK symbol
    return np.array(symbols), processed_bitstream
