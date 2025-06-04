import numpy as np

def qpsk_demodulate(noisy_symbols):
    """
    Demodulates noisy QPSK symbols back to a bitstream.
    """
    if len(noisy_symbols) == 0:
        return ""

    constellation_points = np.array([
        (1 + 1j) / np.sqrt(2),  
        (-1 + 1j) / np.sqrt(2), 
        (-1 - 1j) / np.sqrt(2), 
        (1 - 1j) / np.sqrt(2)   
    ])
    dibit_map = ['00', '01', '10', '11'] 
    
    received_bitstream = ""
    for symbol in noisy_symbols:
        distances = np.abs(symbol - constellation_points)
        chosen_index = np.argmin(distances)
        received_bitstream += dibit_map[chosen_index]
    return received_bitstream