from utils.cross_correlation import crosscorr_2d, crosscorr_2d_color
from utils.constants import OUTPUTPATH, BASEPATH, FINGERPRINTSPATH_ANONYMIZATION
from utils.rotate_image import rotate_image, rotate_back_image
from utils.pce import pce, pce_color
import numpy as np
import glob
import cv2
import os

PRINT = True

def print_status(message: str) -> None:
    if PRINT:
        print(message)

def median_filter(image, kernel_size: int):
    # cv2.medianBlur only accepts a single kernel size (assumes square kernel)
    return cv2.medianBlur(image, kernel_size)

def main(devices: list[str]) -> None:
    base_path = os.path.join(BASEPATH, 'D')
    save_path = os.path.join(OUTPUTPATH, 'median_filtering', 'D')
    fingerprint_base = os.path.join(FINGERPRINTSPATH_ANONYMIZATION, "Fingerprint_D")

    for device in devices:
        # Cache fingerprint for the device (load it once)
        device_fingerprint_file = os.path.join(fingerprint_base+f"{device}.npy")
        fingerprint = np.load(device_fingerprint_file)
        fingerprint = np.repeat(fingerprint[..., np.newaxis], 3, axis=2)

        # Create device save folder if it does not exist
        device_save_path = os.path.join(save_path + device)
        os.makedirs(device_save_path, exist_ok=True)

        files = sorted(glob.glob(os.path.join(base_path + device, 'nat', '*.*')))
        for img_path in files:
            print_status(img_path)
            # Build the output image path; uses last 18 characters of original file name
            save_path_image = os.path.join(device_save_path, os.path.basename(img_path)[-18:])

            img = cv2.imread(img_path)
            if img is None:
                continue
            img = rotate_image(img, img_path)
            
            # Apply median filtering
            img_anonymized = median_filter(img, 3)
            
            # Initialize parameters for noise correction
            alpha_0, alpha_1 = 0, 1
            v_pce = pce_color(crosscorr_2d_color(img_anonymized, fingerprint))
            print_status(v_pce)
            iteration = 0
            
            # Loop until the condition is met or maximum iterations reached
            while v_pce > 50 and iteration < 10:
                alpha_2 = alpha_1 + (alpha_1 - alpha_0) / 10
                alpha_0, alpha_1 = alpha_1, alpha_2
                
                # Vectorized noise correction over all channels
                noise_residual = img - img_anonymized
                img_anonymized = img - alpha_2 * noise_residual

                v_pce = pce_color(crosscorr_2d_color(img_anonymized, fingerprint))
                print_status(v_pce)
                iteration += 1

            img_anonymized = rotate_back_image(img_anonymized, img_path)
            if not img_anonymized is None:
                cv2.imwrite(save_path_image, img_anonymized)
