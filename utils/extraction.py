from multiprocessing import Pool, cpu_count
from sklearn.metrics import roc_curve, auc
from numpy.fft import fft2, ifft2
from scipy.ndimage import filters
from tqdm import tqdm
import numpy as np
import pywt

class ArgumentError(Exception):
    pass

"""
Extraction functions
"""

def extract_single(im: np.ndarray,
                   levels: int = 4,
                   sigma: float = 5,
                   wdft_sigma: float = 0) -> np.ndarray:
    """
    Extract noise residual from a single image
    :param im: grayscale or color image, np.uint8
    :param levels: number of wavelet decomposition levels
    :param sigma: estimated noise power
    :param wdft_sigma: estimated DFT noise power
    :return: noise residual
    """

    W = noise_extract(im, levels, sigma)
    W = rgb2gray(W)
    W = zero_mean_total(W)
    W_std = W.std(ddof=1) if wdft_sigma == 0 else wdft_sigma
    W = wiener_dft(W, W_std).astype(np.float32)

    return W


def noise_extract(im: np.ndarray, levels: int = 4, sigma: float = 5) -> np.ndarray:
    """
    NoiseExtract as from Binghamton toolbox.

    :param im: grayscale or color image, np.uint8
    :param levels: number of wavelet decomposition levels
    :param sigma: estimated noise power
    :return: noise residual
    """

    assert (im.dtype == np.uint8)
    assert (im.ndim in [2, 3])

    im = im.astype(np.float32)

    noise_var = sigma ** 2

    if im.ndim == 2:
        im.shape += (1,)

    W = np.zeros(im.shape, np.float32)

    for ch in range(im.shape[2]):

        wlet = None
        while wlet is None and levels > 0:
            try:
                wlet = pywt.wavedec2(im[:, :, ch], 'db4', level=levels)
            except ValueError:
                levels -= 1
                wlet = None
        if wlet is None:
            raise ValueError('Impossible to compute Wavelet filtering for input size: {}'.format(im.shape))

        wlet_details = wlet[1:]

        wlet_details_filter = [None] * len(wlet_details)
        # Cycle over Wavelet levels 1:levels-1
        for wlet_level_idx, wlet_level in enumerate(wlet_details):
            # Cycle over H,V,D components
            level_coeff_filt = [None] * 3
            for wlet_coeff_idx, wlet_coeff in enumerate(wlet_level):
                level_coeff_filt[wlet_coeff_idx] = wiener_adaptive(wlet_coeff, noise_var)
            wlet_details_filter[wlet_level_idx] = tuple(level_coeff_filt)

        # Set filtered detail coefficients for Levels > 0 ---
        wlet[1:] = wlet_details_filter

        # Set to 0 all Level 0 approximation coefficients ---
        wlet[0][...] = 0

        # Invert wavelet transform ---
        wrec = pywt.waverec2(wlet, 'db4')
        try:
            W[:, :, ch] = wrec
        except ValueError:
            W = np.zeros(wrec.shape[:2] + (im.shape[2],), np.float32)
            W[:, :, ch] = wrec

    if W.shape[2] == 1:
        W.shape = W.shape[:2]

    W = W[:im.shape[0], :im.shape[1]]

    return W


def noise_extract_compact(args):
    """
    Extract residual, multiplied by the image. Useful to save memory in multiprocessing operations
    :param args: (im, levels, sigma), see noise_extract for usage
    :return: residual, multiplied by the image
    """
    w = noise_extract(*args)
    im = args[0]
    return (w * im / 255.).astype(np.float32)


def extract_multiple_aligned(imgs: list, levels: int = 4, sigma: float = 5, processes: int = None,
                             batch_size=cpu_count(), tqdm_str: str = '') -> np.ndarray:
    """
    Extract PRNU from a list of images. Images are supposed to be the same size and properly oriented
    :param tqdm_str: tqdm description (see tqdm documentation)
    :param batch_size: number of parallel processed images
    :param processes: number of parallel processes
    :param imgs: list of images of size (H,W,Ch) and type np.uint8
    :param levels: number of wavelet decomposition levels
    :param sigma: estimated noise power
    :return: PRNU
    """
    assert (isinstance(imgs[0], np.ndarray))
    assert (imgs[0].ndim == 3)
    assert (imgs[0].dtype == np.uint8)

    h, w, ch = imgs[0].shape

    RPsum = np.zeros((h, w, ch), np.float32)
    NN = np.zeros((h, w, ch), np.float32)

    if processes is None or processes > 1:
        args_list = []
        for im in imgs:
            args_list += [(im, levels, sigma)]
        pool = Pool(processes)

        for batch_idx0 in tqdm(np.arange(start=0, step=batch_size, stop=len(imgs)), disable=tqdm_str == '',
                               desc=(tqdm_str + ' (1/2)'), dynamic_ncols=True):
            # print(batch_idx0, batch_size)
            nni = pool.map(inten_sat_compact, args_list[batch_idx0:batch_idx0 + batch_size])
            for ni in nni:
                NN += ni
            del nni

        for batch_idx0 in tqdm(np.arange(start=0, step=batch_size, stop=len(imgs)), disable=tqdm_str == '',
                               desc=(tqdm_str + ' (2/2)'), dynamic_ncols=True):
            wi_list = pool.map(noise_extract_compact, args_list[batch_idx0:batch_idx0 + batch_size])
            for wi in wi_list:
                RPsum += wi
            del wi_list

        pool.close()

    else:  # Single process
        for im in tqdm(imgs, disable=tqdm_str is None, desc=tqdm_str, dynamic_ncols=True):
            RPsum += noise_extract_compact((im, levels, sigma))
            NN += (inten_scale(im) * saturation(im)) ** 2

    K = RPsum / (NN + 1)
    K = rgb2gray(K)
    K = zero_mean_total(K)
    K = wiener_dft(K, K.std(ddof=1)).astype(np.float32)

    return K


def cut_ctr(array: np.ndarray, sizes: tuple) -> np.ndarray:
    """
    Cut a multi-dimensional array at its center, according to sizes
    :param array: multidimensional array
    :param sizes: tuple of the same length as array.ndim
    :return: multidimensional array, center cut
    """
    array = array.copy()
    if not (array.ndim == len(sizes)):
        raise ArgumentError('array.ndim must be equal to len(sizes)')
    for axis in range(array.ndim):
        axis_target_size = sizes[axis]
        axis_original_size = array.shape[axis]
        if axis_target_size > axis_original_size:
            raise ValueError(
                'Can\'t have target size {} for axis {} with original size {}'.format(axis_target_size, axis,
                                                                                      axis_original_size))
        elif axis_target_size < axis_original_size:
            axis_start_idx = (axis_original_size - axis_target_size) // 2
            axis_end_idx = axis_start_idx + axis_target_size
            array = np.take(array, np.arange(axis_start_idx, axis_end_idx), axis)
    return array


def wiener_dft(im: np.ndarray, sigma: float) -> np.ndarray:
    """
    Adaptive Wiener filter applied to the 2D FFT of the image
    :param im: multidimensional array
    :param sigma: estimated noise power
    :return: filtered version of input im
    """
    noise_var = sigma ** 2
    h, w = im.shape

    im_noise_fft = fft2(im)
    im_noise_fft_mag = np.abs(im_noise_fft / (h * w) ** .5)

    im_noise_fft_mag_noise = wiener_adaptive(im_noise_fft_mag, noise_var)

    zeros_y, zeros_x = np.nonzero(im_noise_fft_mag == 0)

    im_noise_fft_mag[zeros_y, zeros_x] = 1
    im_noise_fft_mag_noise[zeros_y, zeros_x] = 0

    im_noise_fft_filt = im_noise_fft * im_noise_fft_mag_noise / im_noise_fft_mag
    im_noise_filt = np.real(ifft2(im_noise_fft_filt))

    return im_noise_filt.astype(np.float32)


def zero_mean(im: np.ndarray) -> np.ndarray:
    """
    ZeroMean called with the 'both' argument, as from Binghamton toolbox.
    :param im: multidimensional array
    :return: zero mean version of input im
    """
    # Adapt the shape ---
    if im.ndim == 2:
        im.shape += (1,)

    h, w, ch = im.shape

    # Subtract the 2D mean from each color channel ---
    ch_mean = im.mean(axis=0).mean(axis=0)
    ch_mean.shape = (1, 1, ch)
    i_zm = im - ch_mean

    # Compute the 1D mean along each row and each column, then subtract ---
    row_mean = i_zm.mean(axis=1)
    col_mean = i_zm.mean(axis=0)

    row_mean.shape = (h, 1, ch)
    col_mean.shape = (1, w, ch)

    i_zm_r = i_zm - row_mean
    i_zm_rc = i_zm_r - col_mean

    # Restore the shape ---
    if im.shape[2] == 1:
        i_zm_rc.shape = im.shape[:2]

    return i_zm_rc


def zero_mean_total(im: np.ndarray) -> np.ndarray:
    """
    ZeroMeanTotal as from Binghamton toolbox.
    :param im: multidimensional array
    :return: zero mean version of input im
    """
    im[0::2, 0::2] = zero_mean(im[0::2, 0::2])
    im[1::2, 0::2] = zero_mean(im[1::2, 0::2])
    im[0::2, 1::2] = zero_mean(im[0::2, 1::2])
    im[1::2, 1::2] = zero_mean(im[1::2, 1::2])
    return im


def rgb2gray(im: np.ndarray) -> np.ndarray:
    """
    RGB to gray as from Binghamton toolbox.
    :param im: multidimensional array
    :return: grayscale version of input im
    """
    rgb2gray_vector = np.asarray([0.29893602, 0.58704307, 0.11402090]).astype(np.float32)
    rgb2gray_vector.shape = (3, 1)

    if im.ndim == 2:
        im_gray = np.copy(im)
    elif im.shape[2] == 1:
        im_gray = np.copy(im[:, :, 0])
    elif im.shape[2] == 3:
        w, h = im.shape[:2]
        im = np.reshape(im, (w * h, 3))
        im_gray = np.dot(im, rgb2gray_vector)
        im_gray.shape = (w, h)
    else:
        raise ValueError('Input image must have 1 or 3 channels')

    return im_gray.astype(np.float32)


def threshold(wlet_coeff_energy_avg: np.ndarray, noise_var: float) -> np.ndarray:
    """
    Noise variance theshold as from Binghamton toolbox.
    :param wlet_coeff_energy_avg:
    :param noise_var:
    :return: noise variance threshold
    """
    res = wlet_coeff_energy_avg - noise_var
    return (res + np.abs(res)) / 2


def wiener_adaptive(x: np.ndarray, noise_var: float, **kwargs) -> np.ndarray:
    """
    WaveNoise as from Binghamton toolbox.
    Wiener adaptive flter aimed at extracting the noise component
    For each input pixel the average variance over a neighborhoods of different window sizes is first computed.
    The smaller average variance is taken into account when filtering according to Wiener.
    :param x: 2D matrix
    :param noise_var: Power spectral density of the noise we wish to extract (S)
    :param window_size_list: list of window sizes
    :return: wiener filtered version of input x
    """
    window_size_list = list(kwargs.pop('window_size_list', [3, 5, 7, 9]))

    energy = x ** 2

    avg_win_energy = np.zeros(x.shape + (len(window_size_list),))
    for window_idx, window_size in enumerate(window_size_list):
        avg_win_energy[:, :, window_idx] = filters.uniform_filter(energy,
                                                                  window_size,
                                                                  mode='constant')

    coef_var = threshold(avg_win_energy, noise_var)
    coef_var_min = np.min(coef_var, axis=2)

    x = x * noise_var / (coef_var_min + noise_var)

    return x


def inten_scale(im: np.ndarray) -> np.ndarray:
    """
    IntenScale as from Binghamton toolbox
    :param im: type np.uint8
    :return: intensity scaled version of input x
    """

    assert (im.dtype == np.uint8)

    T = 252
    v = 6
    # print(im, v, T)
    arg = (-((im-T)**2))/ v
    # print(arg)
    out = np.exp(arg)
    # out = np.exp(-1 * (im - T) ** 2 / v)
    
    out[im < T] = im[im < T] / T
    
    return out


def saturation(im: np.ndarray) -> np.ndarray:
    """
    Saturation as from Binghamton toolbox
    :param im: type np.uint8
    :return: saturation map from input im
    """
    assert (im.dtype == np.uint8)

    if im.ndim == 2:
        im.shape += (1,)

    h, w, ch = im.shape

    if im.max() < 250:
        return np.ones((h, w, ch))

    im_h = im - np.roll(im, (0, 1), (0, 1))
    im_v = im - np.roll(im, (1, 0), (0, 1))
    satur_map = \
        np.bitwise_not(
            np.bitwise_and(
                np.bitwise_and(
                    np.bitwise_and(
                        im_h != 0, im_v != 0
                    ), np.roll(im_h, (0, -1), (0, 1)) != 0
                ), np.roll(im_v, (-1, 0), (0, 1)) != 0
            )
        )

    max_ch = im.max(axis=0).max(axis=0)

    for ch_idx, max_c in enumerate(max_ch):
        if max_c > 250:
            satur_map[:, :, ch_idx] = \
                np.bitwise_not(
                    np.bitwise_and(
                        im[:, :, ch_idx] == max_c, satur_map[:, :, ch_idx]
                    )
                )

    return satur_map


def inten_sat_compact(args):
    """
    Memory saving version of inten_scale followed by saturation. Useful for multiprocessing
    :param args:
    :return: intensity scale and saturation of input
    """
    im = args[0]
    return ((inten_scale(im) * saturation(im)) ** 2).astype(np.float32)