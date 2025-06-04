import numpy as np

def add_awgn(symbols, snr_ebn0_db):
    """
    Adds Additive White Gaussian Noise to QPSK symbols.
    snr_ebn0_db: Eb/N0 ratio in dB.
    """
    if len(symbols) == 0:
        return np.array([])

    Es = np.mean(np.abs(symbols)**2) 
    k_bits_per_symbol = 2 
    Eb = Es / k_bits_per_symbol 

    ebn0_linear = 10**(snr_ebn0_db / 10.0)
    
    if ebn0_linear == 0 : 
        N0 = np.inf
    else:
        N0 = Eb / ebn0_linear
    
    if N0 == np.inf: 
        sigma_n = 1e6 # Represent very high noise for SNR = -inf dB
    elif N0 == 0: # No noise if SNR is +inf dB
        sigma_n = 0.0
    else:
        sigma_n = np.sqrt(N0 / 2.0)
    
    noise = sigma_n * (np.random.randn(len(symbols)) + 1j * np.random.randn(len(symbols)))
    return symbols + noise