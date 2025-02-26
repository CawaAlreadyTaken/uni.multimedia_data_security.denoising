
import glob
import cv2
from utils.pce import pce, pce_color
from utils.cross_correlation import crosscorr_2d, crosscorr_2d_color
from utils.rotate_image import rotate_image, rotate_back_image
from utils.constants import OUTPUTPATH, BASEPATH, FINGERPRINTSPATH
import numpy as np
import os

PRINT = True

def _print(stringa: str) -> None:
    if PRINT:
        print(stringa)


def median(img, kernel_size):
    attacked = cv2.medianBlur(img, kernel_size) # it takes only one argument because it considers it squared
    return attacked

def main(devices: list[str]) -> None:

    basepath = BASEPATH + 'D'
    savepath = OUTPUTPATH + 'median_filtering/D'
    fingerprint_path = FINGERPRINTSPATH + "Fingerprint_D"

    for device in devices:

        files = sorted(glob.glob(basepath + device + '/nat/*.*'))
        try:
            os.mkdir(savepath+device)
        except:
            pass
        
        for img_name in files:
                _print(img_name)
                savepath_image = savepath + device + "/" + img_name[-18:]
                # img = cv2.imread(img_name, cv2.IMREAD_GRAYSCALE).astype(np.float32)
                img = cv2.imread(img_name)
                img = rotate_image(img, img_name)
                if img is None: 
                    continue
                device_fingerprint_path = fingerprint_path + device + ".npy" 
                # print(device_fingerprint_path)
                fingerprint = np.load(device_fingerprint_path)
                fingerprint = np.repeat(fingerprint[..., np.newaxis], 3, axis=2)

                # median filtering
                img_anonymized = median(img, 3)

                alpha_0 = 0
                alpha_1 = 1
                alpha_2 = 0
                # v_pce = pce(crosscorr_2d(img, fingerprint)) # I dunno why it uses the real one
                v_pce = pce_color(crosscorr_2d_color(img_anonymized, fingerprint))
                # print(img)
                _print(v_pce)
                iter = 0
                while (v_pce>50 and iter<10):
                    for i in range(0,3):
                        noise_residual = img[:,:,i] - img_anonymized[:,:,i]
                        alpha_2 = alpha_1 + (alpha_1-alpha_0)/10
                        alpha_0 = alpha_1
                        alpha_1 = alpha_2
                        noise_residual_first = alpha_2* noise_residual
                        img_anonymized[:,:,i] = img[:,:,i] - noise_residual_first
                        # v_pce = pce(crosscorr_2d(img_anonymized, fingerprint))
                    v_pce = pce_color(crosscorr_2d_color(img_anonymized, fingerprint))
                    _print(v_pce)
                    iter= iter +1

                img_anonymized = rotate_back_image(img_anonymized, img_name)
                cv2.imwrite(savepath_image , img_anonymized)

