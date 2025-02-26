import numpy as np

# Cross-correlation norm
def ccn_fft(x, y, neighbors=30):
    """
    Computes the quantity c(x, y) in a more efficient way using FFT:
    
    c(x, y) = r_xy(0) / sqrt( (Σ_{m not in [0..neighbors]} [r_xy(m)]^2 ) / (N - neighbors) )

    where r_xy(m) = (1/N) * Σ_{i=0}^{N-1} x[i] * y[(i+m) mod N].
    """
    x = np.ravel(x).astype(np.float32)
    y = np.ravel(y).astype(np.float32)
    N = len(x)
    
    X = np.fft.fft(x)
    Y = np.fft.fft(y)
    
    # R[m] = Σ x[i] * y[(i+m) mod N]
    R = np.fft.ifft(X * np.conjugate(Y))
    
    # May have very small imaginary parts, so we take the real part
    R = R.real
    
    # r_xy(m) = R[m] / N
    # Numerator: r_xy(0) = R[0] / N
    num = R[0] / N
    
    # => sum R[m]^2 / N^2 (for m = neighbors+1..N-1)
    sum_R_sq = np.sum(R[neighbors+1:]**2)  # sum of R[m]^2
    sum_r_xy_sq = sum_R_sq / (N**2)
    
    den = np.sqrt(sum_r_xy_sq / (N - neighbors))
    
    return num / den