from utils.constants import BASEPATH, OUTPUTPATH, FINGERPRINTSPATH
from utils.rotate_image import rotate_image, rotate_back_image
from utils.cross_correlation import crosscorr_2d_color
from skimage.restoration import denoise_wavelet
from utils.pce import pce_color
from utils.ccn import ccn_fft
import numpy as np
import glob
import cv2
import os

def main(devices_list: list[str]):
    alpha_min = 0.008
    alpha_max = 0.04
    threshold_T = 0.1
    max_iters = 10

    devices = sorted(glob.glob(BASEPATH+'D*'))

    for device_path in devices:
        if device_path[-2:] not in devices_list:
            continue
        files = sorted(glob.glob(device_path + '/nat/*.*'))
        output_folder = OUTPUTPATH + 'fingerprint_removal/D' + device_path[-2:] + '/'
        fingerprints_file = FINGERPRINTSPATH + 'Fingerprint_D' + device_path[-2:] + '.npy'
        estimated_fingerprint = np.load(fingerprints_file)
        for img_name in files:
            # Load 'original_image' and 'estimated_fingerprint' as NumPy arrays.
            print(f"[ANONYMIZING fingerprint_removal] {img_name}")
            # original_image = cv2.imread(img_name, cv2.IMREAD_GRAYSCALE).astype(np.float32)
            original_image = cv2.imread(img_name).astype(np.float32)
            original_image = rotate_image(original_image, img_name)
            if original_image is None:
                continue

            altered = remove_camera_fingerprint(
                original_image,
                estimated_fingerprint,
                alpha_min,
                alpha_max,
                threshold_T,
                max_iters
            )

            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            # Save 'altered'
            cv2.imwrite(output_folder + img_name.split('/')[-1], rotate_back_image(altered, img_name))

def denoise_image(img):
    """
    Stronger denoiser using wavelet-based denoising from scikit-image.
    This extracts a noise residue x(I) = I - F(I).
    
    Arguments:
        img: Input image as a NumPy array (H x W x C), typically uint8.

    Returns:
        residual: The noise residual, with same shape as `img`.
    """
    # Convert to float32 for safer arithmetic
    img_f = img.astype(np.float32)

    # Wavelet-based denoising
    #   - method='BayesShrink' or 'VisuShrink' can be chosen. 
    denoised = denoise_wavelet(
        img_f,
        channel_axis=-1,
        convert2ycbcr=True,
        method='BayesShrink',
        mode='soft'
    )

    # Noise residual: x(I) = I - denoise(I)
    residual = img_f - denoised

    return residual

def r_xy_m(x, y, m):
    return np.mean(x * np.roll(y, m))
    result = 0
    for i in range(len(x)):
        result += x[i] * y[(i+m) % len(x)]
    return result / len(x)

def ccn(x, y):
    """
    Computes a correlation over circular cross-correlation norm
    c(x, y) = r_xy(0) / sqrt( (Σ_{m in A} [r_xy(m)]^2) / (L-|A|) )
    """
    x = x.flatten().astype(np.float32)
    y = y.flatten().astype(np.float32)

    neighbors = 30
    num = r_xy_m(x, y, 0)
    den = 0
    print(f"Dovro' farne {len(x)}")
    for m in range(0, len(x)):
        print(m)
        if m not in range(neighbors+1):
            den += r_xy_m(x, y, m) ** 2
    den = np.sqrt(den / (len(x) - neighbors))

    return num / den

def ccn_paper(x, y, neighbors=30):
    """
    Compute the correlation statistic c(x, y) = r_xy(0) / sqrt( ( Σ_{m in A} [r_xy(m)]^2 ) / (L - |A| ) ),
    where r_xy(m) is the circular cross-correlation at lag m.

    Args:
        x, y: 1D or multi-D numpy arrays. Flattened internally.
        neighbors: How many "lags" to include on each side of m=0 in the set A.
                   For example, neighbors=2 => A = {-2, -1, 1, 2}.

    Returns:
        A scalar float representing c(x, y).
    """
    # Flatten and convert to double precision for safety
    x = x.flatten().astype(np.float64)
    y = y.flatten().astype(np.float64)
    L = len(x)
    
    # Compute circular cross-correlation using FFT
    # (r_xy(m) = IFFT( FFT(x) * conj(FFT(y)) )[m], normalized by L)
    X = np.fft.fft(x)
    Y = np.fft.fft(y)
    cc = np.fft.ifft(X * np.conj(Y)).real    # shape (L,)
    cc /= L  # so that r_xy(m) = (1/L)*Σ x_i y_{(i+m)%L}

    # r_xy(0) is the main correlation at zero lag
    r0 = cc[0]

    # Build the set A of nearby lags around zero: {-neighbors..-1, +1..neighbors}
    # We'll map them into valid indices mod L
    lags = np.arange(neighbors + 1, L)
    # The paper sums r_xy(m)^2 for m in A, ignoring m=0
    sum_sq = np.sum(cc[lags]**2)
    # The denominator is sqrt( sum_sq / (L - |A|) )
    denom = np.sqrt(sum_sq / (L - len(lags)))

    # Finally c(x, y) = r_xy(0) / denom
    return r0 / denom

def remove_camera_fingerprint(
    image: np.ndarray,
    fingerprint: np.ndarray,
    alpha_min: float,
    alpha_max: float,
    T: float,
    max_iterations: int
) -> np.ndarray:
    """
    Implements the PRNU (camera fingerprint) removal attack as described
    in the paper. The function iteratively searches for a strength alpha
    that reduces the correlation of the altered image with the estimated
    fingerprint below a threshold T.

    Parameters:
    -----------
    image         : np.ndarray
        The original (unaltered) input image, shape (H, W) or (H, W, C).
    fingerprint   : np.ndarray
        The estimated PRNU fingerprint for the camera. Must match
        the shape of the image or be broadcastable.
    alpha_min     : float
        The initial minimum strength for the search range.
    alpha_max     : float
        The initial maximum strength for the search range.
    T             : float
        The absolute correlation threshold below which we say
        "the fingerprint is removed".
    max_iterations: int
        The maximum number of iterations to try before stopping.

    Returns:
    --------
    np.ndarray
        The altered image whose correlation with 'fingerprint'
        is reduced below T, or the best we could achieve after
        'max_iterations' steps.
    """
    # Copy the input so as not to overwrite
    J = image.astype(np.float32).copy()
    if image.ndim == 3 and fingerprint.ndim == 2:
        fingerprint = np.repeat(fingerprint[..., np.newaxis], 3, axis=2)
    K = fingerprint.astype(np.float32)

    # A helper to compute the correlation c(x(J'), J'*K) from the paper.
    def correlation_metric(J_prime):
        """
        Computes abs( c( x(J'), J'*K ) ),
        where x(J') is the noise residual of J',
        and J'*K is the element-wise product.
        """
        # Noise residual x(J')
        x_Jp = denoise_image(J_prime)  # x(J')
        # Multiply J' * K
        product = J_prime * K
        # Correlation c( x(J'), J'*K )
        ccnfft = ccn_paper(x_Jp, product)
        return abs(ccnfft)

    # Initialize
    best_image = J.copy()
    best_corr = correlation_metric(best_image)
    print(f"Best corr: {best_corr}")
    print(f"Pce prima: {pce_color(crosscorr_2d_color(best_image, fingerprint))}")

    changed_max = False
    changed_min = False
    J_max = J * (1.0 - alpha_max * K)
    J_min = J * (1.0 - alpha_min * K)
    corr_max = correlation_metric(J_max)
    corr_min = correlation_metric(J_min)

    # Iteratively search for alpha
    for _ in range(max_iterations):
        # Candidate with alpha_max
        if changed_max:
            J_max = J * (1.0 - alpha_max * K)
            corr_max = correlation_metric(J_max)
            changed_max = False
        print(f"corr_max: {corr_max}")

        if corr_max < T:
            best_image = J_max
            break  # We've satisfied the threshold

        # Candidate with alpha_min
        if changed_min:
            J_min = J * (1.0 - alpha_min * K)
            corr_min = correlation_metric(J_min)
            changed_min = False
        print(f"corr_min: {corr_min}")

        if corr_min < T:
            best_image = J_min
            break  # We've satisfied the threshold

        # Decide which side to shrink based on which correlation is lower
        if corr_min < corr_max:
            # We lean toward alpha_min
            changed_max = True
            alpha_max = 0.5 * (alpha_min + alpha_max)
            if corr_min < best_corr:
                best_image = J_min
                best_corr = corr_min
        else:
            # We lean toward alpha_max
            changed_min = True
            alpha_min = 0.5 * (alpha_min + alpha_max)
            if corr_max < best_corr:
                best_image = J_max
                best_corr = corr_max

    print(f"Pce dopo: {pce_color(crosscorr_2d_color(best_image, fingerprint))}")
    return best_image.astype(np.uint8)
