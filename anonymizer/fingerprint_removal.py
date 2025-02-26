from utils.cross_correlation import crosscorr_2d_color
from utils.rotate_image import rotate_image
from utils.constants import BASEPATH
from utils.pce import pce_color
from utils.ccn import ccn_fft
import numpy as np
import glob
import cv2

def main(devices_list: list[str]):
    alpha_min = 0.01
    alpha_max = 1.0
    threshold_T = 35.0
    max_iters = 10

    devices = sorted(glob.glob(BASEPATH+'D*'))

    for device_path in devices:
        if device_path[-2:] not in devices_list:
            continue
        files = sorted(glob.glob(device_path + '/nat/*.*'))
        for img_name in files:
            # Load 'original_image' and 'estimated_fingerprint' as NumPy arrays.
            print(f"[ANONYMIZING fingerprint_removal] {img_name}")
            # original_image = cv2.imread(img_name, cv2.IMREAD_GRAYSCALE).astype(np.float32)
            original_image = cv2.imread(img_name).astype(np.float32)
            original_image = rotate_image(original_image, img_name)
            if original_image is None:
                continue
            estimated_fingerprint = np.load(f"fingerprints/Fingerprint_D{device_path[-2:]}.npy")

            altered = remove_camera_fingerprint(
                original_image,
                estimated_fingerprint,
                alpha_min,
                alpha_max,
                threshold_T,
                max_iters
            )

            # Save or display 'altered'
            cv2.imwrite("altered_image.png", altered)

def denoise_image(img):
    """
    Placeholder for a denoising function F in the paper (Eq. 2).
    In practice, you might use a wavelet-based denoiser, BM3D, or
    another robust image-denoising method to extract the noise residue.

    For this simple example, we'll just apply a small Gaussian blur
    and subtract it, but you should replace this with a stronger denoiser
    to get more accurate noise residues.
    """
    # Convert to float32 for safer arithmetic
    img_f = img.astype(np.float32)
    # Simple Gaussian blur
    blurred = cv2.GaussianBlur(img_f, ksize=(3, 3), sigmaX=1.0)
    # Noise residual x(I) = I - denoise(I)
    residual = img_f - blurred
    return residual

# def r_xy_m(x, y, m):
#     result = 0
#     for i in range(len(x)):
#         result += x[i] * y[(i+m) % len(x)]
#     return result / len(x)
#     
# 
# def ccn(x, y):
#     """
#     Computes a correlation over circular cross-correlation norm
#     c(x, y) = r_xy(0) / sqrt( (Σ_{m in A} [r_xy(m)]^2) / (L-|A|) )
#     """
#     x = x.flatten().astype(np.float32)
#     y = y.flatten().astype(np.float32)
# 
#     neighbors = 30
#     num = r_xy_m(x, y, 0)
#     den = 0
#     for m in range(0, len(x)):
#         print(m)
#         if m not in range(neighbors+1):
#             den += r_xy_m(x, y, m) ** 2
#     den = np.sqrt(den / (len(x) - neighbors))
# 
#     return num / den

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
        return abs(ccn_fft(x_Jp, product))

    # Initialize
    best_image = J.copy()
    best_corr = correlation_metric(best_image)
    print(f"Pce prima: {pce_color(crosscorr_2d_color(best_image, fingerprint))}")

    # Iteratively search for alpha
    for _ in range(max_iterations):
        # Candidate with alpha_max
        J_max = J * (1.0 - alpha_max * K)
        corr_max = correlation_metric(J_max)
        print(corr_max)

        if corr_max < T:
            best_image = J_max
            break  # We've satisfied the threshold

        # Candidate with alpha_min
        J_min = J * (1.0 - alpha_min * K)
        corr_min = correlation_metric(J_min)

        if corr_min < T:
            best_image = J_min
            break  # We've satisfied the threshold

        # Decide which side to shrink based on which correlation is lower
        if corr_min < corr_max:
            # We lean toward alpha_min
            alpha_max = 0.5 * (alpha_min + alpha_max)
            if corr_min < best_corr:
                best_corr = corr_min
                best_image = J_min
        else:
            # We lean toward alpha_max
            alpha_min = 0.5 * (alpha_min + alpha_max)
            if corr_max < best_corr:
                best_corr = corr_max
                best_image = J_max

    print(f"Pce dopo: {pce_color(crosscorr_2d_color(best_image, fingerprint))}")
    return best_image.astype(np.uint8)
