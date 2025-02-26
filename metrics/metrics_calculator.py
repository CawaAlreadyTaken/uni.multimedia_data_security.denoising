from utils.constants import BASEPATH, FINGERPRINTSPATH
from utils.cross_correlation import crosscorr_2d_color
from utils.rotate_image import rotate_image
from utils.pce import pce_color
from utils.ccn import ccn_fft
from utils.wpsnr import wpsnr
import numpy as np
import glob
import json
import cv2
import os


def main(chosen_devices: list[str], anonymized_images: str):
    for device in chosen_devices:
        files = sorted(glob.glob(BASEPATH +'D'+ device +'/nat/*.*'))

        fingerprint = np.load(FINGERPRINTSPATH + 'Fingerprint_D'+device+'.npy').astype(np.float32)
        fingerprint = np.repeat(fingerprint[..., np.newaxis], 3, axis=2)

        if not os.path.exists(anonymized_images):
            print(anonymized_images+" folder does not exist")
            return

        data = {}

        for original_path in files:
            data_file = {}
            anonymized_path = anonymized_images+'/D'+device+'/'+original_path.split("/")[-1]

            if not os.path.exists(anonymized_path):
                continue

            original = cv2.imread(original_path).astype(np.float32)
            original = rotate_image(original, original_path)

            if original is None:
                continue

            anonymized = cv2.imread(anonymized_path).astype(np.float32)
            anonymized = rotate_image(anonymized, original_path)

            if anonymized is None:
                continue
            
            print("computing file: ", original_path)

            print("computing wpsnr")
            data_file['wpsnr'] = wpsnr(original, anonymized)
            print("computing initial_pce")
            data_file['initial_pce'] = pce_color(crosscorr_2d_color(original, fingerprint))
            print("computing pce")
            data_file['pce'] = pce_color(crosscorr_2d_color(anonymized, fingerprint))
            print("computing initial_ccn")
            data_file['initial_ccn'] = ccn_fft(original,fingerprint)
            print("computing ccn")
            data_file['ccn'] = ccn_fft(anonymized, fingerprint)

            data[original_path.split("/")[-1]] = data_file
            print(json.dumps(data_file, indent=4, ensure_ascii=False))
        
        output_file = anonymized_images+'/D'+device+'/'+'metrics.json'
        print("saving file: ", output_file)
        with open(output_file, "w", encoding="utf-8") as file_json:
            json.dump(data, file_json, indent=4, ensure_ascii=False)

    
