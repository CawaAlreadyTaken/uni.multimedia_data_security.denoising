from utils.cross_correlation import crosscorr_2d, crosscorr_2d_color
from utils.constants import BASEPATH, OUTPUTPATH, FINGERPRINTSPATH
from utils.pce import pce, pce_color
from utils.rotate_image import rotate_image, rotate_back_image
import numpy as np
import os
from math import log10

import glob
import pywt
import cv2

def wavelet_denoise(image, wavelet='db8', level=4):
    coeffs = pywt.wavedec2(image, wavelet, level=level)
    coeffs_thresholded = [coeffs[0]] + [(pywt.threshold(cH, np.std(cH), mode='soft'),
                                         pywt.threshold(cV, np.std(cV), mode='soft'),
                                         pywt.threshold(cD, np.std(cD), mode='soft'))
                                        for cH, cV, cD in coeffs[1:]]
    return pywt.waverec2(coeffs_thresholded, wavelet)

def wavelet_denoise_rgb(image, wavelet='db8', level=4):
    denoised_channels = []
    for i in range(3):
        channel = image[:, :, i]
        denoised_channel = wavelet_denoise(channel, wavelet, level)
        denoised_channels.append(denoised_channel)
    
    return np.stack(denoised_channels, axis=2)

def anonymize_image(image, prnu_estimate, threshold=50):
    b = 0.0
    res_pce = 0
    while True:
        noise = image - wavelet_denoise_rgb(image)
        anonymized = image - (log10(b+1) + 0.00001) * noise
        # anonymized = image - (0.0001 * 1.2**b) * noise
        res_pce = pce_color(crosscorr_2d_color(anonymized, prnu_estimate))
        if res_pce < threshold:
            print('pce: ',res_pce,', b: ', b)
            return anonymized
        b += 1

    
def main(chosen_devices: list):
    for device in chosen_devices:
        files = sorted(glob.glob(BASEPATH +'D'+ device +'/nat/*.*'))
        fingerprint = np.load(FINGERPRINTSPATH + 'Fingerprint_D'+device+'.npy').astype(np.float32)
        fingerprint = np.repeat(fingerprint[..., np.newaxis], 3, axis=2)
        output_folder = OUTPUTPATH+'ADP2/D'+device+'/'

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        for file in files:
            print('anonymizing file: ', file)
            file_name = file.split("/")[-1]
            image = cv2.imread(file).astype(np.float32)
            image = rotate_image(image, file)
            if image is None:
                continue


            print('original pce: ',pce_color(crosscorr_2d_color(image, fingerprint)))
            anonymized_image = anonymize_image(image, fingerprint)
            cv2.imwrite(output_folder+file_name, rotate_back_image(anonymized_image,file),[cv2.IMWRITE_JPEG_QUALITY, 100])
            cv2.imwrite(output_folder+"Gray_"+file_name, rotate_back_image(image,file),[cv2.IMWRITE_JPEG_QUALITY, 100])
