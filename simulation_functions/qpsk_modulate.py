import numpy as np

def qpsk_modulate(bitstream):
    """
    Modulates a bitstream using QPSK.
    If bitstream length is odd, the last bit is truncated.
    Returns symbols_array, processed_bitstream.
    """
    processed_bitstream = bitstream
    if len(processed_bitstream) % 2 != 0:
        processed_bitstream = processed_bitstream[:-1] 
        # No print here, truncation is a defined behavior of this function.
        # The GUI should ideally pass an even length bitstream or be aware of this.

    symbols = []
    mapping = {
        '00': (1 + 1j) / np.sqrt(2),
        '01': (-1 + 1j) / np.sqrt(2),
        '10': (-1 - 1j) / np.sqrt(2), 
        '11': (1 - 1j) / np.sqrt(2)  
    }
    for i in range(0, len(processed_bitstream), 2):
        dibit = processed_bitstream[i:i+2]
        if len(dibit) == 2: # Should always be true if processed_bitstream is even and not empty
             symbols.append(mapping[dibit])
    return np.array(symbols), processed_bitstream