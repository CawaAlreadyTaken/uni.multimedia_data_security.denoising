import numpy as np
from numpy.fft import fft2, ifft2

"""
Cross-correlation functions
"""

def crosscorr_2d_color(k1: np.ndarray, k2: np.ndarray) -> np.ndarray:
    """
    Compute the cross-correlation between two color (3D) images/fingerprints.
    Each has shape (height, width, channels). The result is a 2D cross-correlation
    matrix of shape (max_height, max_width).

    :param k1: 3D matrix (H, W, C)
    :param k2: 3D matrix (H, W, C)
    :return: 2D cross-correlation matrix
    """
    # Check input dimensions
    assert k1.ndim == 3 and k2.ndim == 3, "Both inputs must be 3D: (H, W, C)."
    assert k1.shape[2] == k2.shape[2], "Number of channels must match."
    
    # Determine the final correlation map size
    max_height = max(k1.shape[0], k2.shape[0])
    max_width  = max(k1.shape[1], k2.shape[1])
    channels   = k1.shape[2]
    
    # We'll accumulate the cross-correlation from each channel
    cc_sum = np.zeros((max_height, max_width), dtype=np.float32)

    for c in range(channels):
        # Extract single channel
        k1_c = k1[..., c].astype(np.float32)
        k2_c = k2[..., c].astype(np.float32)

        # Subtract mean per channel
        k1_c -= k1_c.mean()
        k2_c -= k2_c.mean()

        # Pad to the same size
        k1_c_padded = np.pad(k1_c,
                             ((0, max_height - k1_c.shape[0]),
                              (0, max_width  - k1_c.shape[1])),
                             mode='constant', constant_values=0)

        k2_c_padded = np.pad(k2_c,
                             ((0, max_height - k2_c.shape[0]),
                              (0, max_width  - k2_c.shape[1])),
                             mode='constant', constant_values=0)

        # FFT of channel 1
        k1_c_fft = fft2(k1_c_padded)
        # FFT of channel 2 rotated by 180 degrees 
        # (equivalent to cross-correlation via convolution)
        k2_c_fft = fft2(np.rot90(k2_c_padded, 2))

        # Inverse FFT of product
        cc_channel = np.real(ifft2(k1_c_fft * k2_c_fft))

        # Accumulate
        cc_sum += cc_channel.astype(np.float32)

    return cc_sum

def crosscorr_2d(k1: np.ndarray, k2: np.ndarray):
    """
    PRNU 2D cross-correlation
    :param k1: 2D matrix of size (h1,w1)
    :param k2: 2D matrix of size (h2,w2)
    :return: 2D matrix of size (max(h1,h2),max(w1,w2))
    """
    
    assert (k1.ndim == 2)
    assert (k2.ndim == 2)

    max_height = max(k1.shape[0], k2.shape[0])
    max_width = max(k1.shape[1], k2.shape[1])

    k1 -= k1.flatten().mean()
    k2 -= k2.flatten().mean()

    k1 = np.pad(k1, [(0, max_height - k1.shape[0]), (0, max_width - k1.shape[1])], mode='constant', constant_values=0)
    k2 = np.pad(k2, [(0, max_height - k2.shape[0]), (0, max_width - k2.shape[1])], mode='constant', constant_values=0)

    k1_fft = fft2(k1, )
    k2_fft = fft2(np.rot90(k2, 2), )

    return np.real(ifft2(k1_fft * k2_fft)).astype(np.float32)


def aligned_cc(k1: np.ndarray, k2: np.ndarray) -> dict:
    """
    Aligned PRNU cross-correlation
    :param k1: (n1,nk) or (n1,nk1,nk2,...)
    :param k2: (n2,nk) or (n2,nk1,nk2,...)
    :return: {'cc':(n1,n2) cross-correlation matrix,'ncc':(n1,n2) normalized cross-correlation matrix}
    """

    # Type cast
    k1 = np.array(k1).astype(np.float32)
    k2 = np.array(k2).astype(np.float32)

    ndim1 = k1.ndim
    ndim2 = k2.ndim
    assert (ndim1 == ndim2)

    k1 = np.ascontiguousarray(k1).reshape(k1.shape[0], -1)
    k2 = np.ascontiguousarray(k2).reshape(k2.shape[0], -1)

    assert (k1.shape[1] == k2.shape[1])

    k1_norm = np.linalg.norm(k1, ord=2, axis=1, keepdims=True)
    k2_norm = np.linalg.norm(k2, ord=2, axis=1, keepdims=True)

    k2t = np.ascontiguousarray(k2.transpose())

    cc = np.matmul(k1, k2t).astype(np.float32)
    ncc = (cc / (k1_norm * k2_norm.transpose())).astype(np.float32)

    return {'cc': cc, 'ncc': ncc}