
import glob
import cv2
from utils.pce import pce
from utils.cross_correlation import crosscorr_2d
from utils.rotate_image import rotate_image, rotate_back_image
import numpy as np

PRINT = False

def _print(stringa: str) -> None:
    if PRINT:
        print(stringa)


def median(img, kernel_size):
    attacked = cv2.medianBlur(img, kernel_size) # it takes only one argument because it considers it squared
    return attacked

def main(devices: list[str]) -> None:

    basepath='/media/SSD_mmlab/VISION_IMAGES/D'
    savepath='anonymized/median_filtering/D'
    fingerprint_path = "fingerprints/Fingerprint_D"

    for device in devices:

        files = sorted(glob.glob(basepath + device + '/nat/*.*'))
        
        for img_name in files:
                _print(img_name)
                savepath_image = savepath + device + "/" + img_name[-18:]
                img = cv2.imread(img_name, cv2.IMREAD_GRAYSCALE).astype(np.float32)
                img = rotate_image(img, img_name)
                device_fingerprint_path = fingerprint_path + device + ".npy" 
                # print(device_fingerprint_path)
                fingerprint = np.load(device_fingerprint_path)

                # median filtering
                img_anonymized = median(img, 3)

                alpha_0 = 0
                alpha_1 = 1
                alpha_2 = 0
                v_pce = pce(crosscorr_2d(img, fingerprint)) # I dunno why it uses the real one
                iter = 0
                while (v_pce>50):
                    noise_residual = img - img_anonymized
                    alpha_2 = alpha_1 + (alpha_1-alpha_0)/10
                    alpha_0 = alpha_1
                    alpha_1 = alpha_2
                    noise_residual_first = alpha_2* noise_residual
                    img_anonymized = img - noise_residual_first
                    v_pce = pce(crosscorr_2d(img_anonymized, fingerprint))
                    _print(v_pce)
                    iter= iter +1

                img_anonymized = rotate_back_image(img_anonymized, img_name)
                cv2.imwrite(savepath_image , img_anonymized.astype(np.uint8))

