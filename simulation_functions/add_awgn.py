import numpy as np

def add_awgn(symbols, snr_ebn0_db):

    if len(symbols) == 0: # Check if symbols is empty
        return np.array([])

    Es = np.mean(np.abs(symbols)**2)  # Average symbol energy
    k_bits_per_symbol = 2 
    Eb = Es / k_bits_per_symbol # Energy per bit 

    ebn0_linear = 10**(snr_ebn0_db / 10.0) # Convert SNR to linear scale
    sigma_n = np.sqrt(Eb / ebn0_linear) # Calculate noise standard deviation
    
    if ebn0_linear == 0 : 
        N0 = np.inf
    else:
        N0 = Eb / ebn0_linear # Noise power spectral density
    
    noise = sigma_n * (np.random.randn(len(symbols)) + 1j * np.random.randn(len(symbols))) # Generate AWGN noise
    return symbols + noise
