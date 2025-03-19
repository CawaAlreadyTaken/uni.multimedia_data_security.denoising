from utils.constants import BASEPATH, FINGERPRINTSPATH
from utils.cross_correlation import crosscorr_2d_color
from utils.rotate_image import rotate_image
from joblib import Parallel, delayed
from utils.pce import pce_color
from utils.ccn import ccn_fft
from utils.wpsnr import wpsnr
import multiprocessing
import numpy as np
import glob
import json
import cv2
import os

def compute_metrics(original_path, anonymized_path, fingerprint):
    if not os.path.exists(anonymized_path):
        return None

    original = cv2.imread(original_path)
    if original is None:
        return None
    
    anonymized = cv2.imread(anonymized_path)
    if anonymized is None:
        return None

    original = rotate_image(original.astype(np.float32), original_path)
    anonymized = rotate_image(anonymized.astype(np.float32), original_path)
    if original is None or anonymized is None:
        return None

    print("Calculating", os.path.basename(original_path))

    results = {}
    results['wpsnr'] = float(wpsnr(original, anonymized))
    results['initial_pce'] = float(pce_color(crosscorr_2d_color(original, fingerprint)))
    results['pce'] = float(pce_color(crosscorr_2d_color(anonymized, fingerprint)))
    results['initial_ccn'] = float(ccn_fft(original, fingerprint))
    results['ccn'] = float(ccn_fft(anonymized, fingerprint))

    return (os.path.basename(original_path), results)

def main(chosen_devices: list[str], anonymized_images: str):
    # n_jobs = multiprocessing.cpu_count()
    n_jobs = 14
    print("Executing with n_jobs =", n_jobs)

    for device in chosen_devices:
        files = sorted(glob.glob(BASEPATH + 'D' + device + '/nat/*.*'))
        
        fp_path = os.path.join(FINGERPRINTSPATH, f'Fingerprint_D{device}.npy')
        fingerprint = np.load(fp_path).astype(np.float32)
        fingerprint = np.repeat(fingerprint[..., np.newaxis], 3, axis=2)

        if not os.path.exists(anonymized_images):
            print(f"{anonymized_images} folder does not exist")
            return

        print(f"\n** Processing device D{device} **")

        tasks = []
        for original_path in files:
            anonymized_path = os.path.join(anonymized_images, f'D{device}', os.path.basename(original_path))
            tasks.append((original_path, anonymized_path))

        results = Parallel(n_jobs=n_jobs)(
            delayed(compute_metrics)(orig, anon, fingerprint) 
            for (orig, anon) in tasks
        )

        results = [r for r in results if r is not None]

        data = {filename: metrics for (filename, metrics) in results}

        output_file = os.path.join(anonymized_images, f'D{device}', 'metrics.json')
        print("Saving file:", output_file)
        with open(output_file, "w", encoding="utf-8") as file_json:
            file_json.write(json.dumps(data, indent=4, ensure_ascii=False))

        print(f" -> D{device} completed, {len(data)} file processed.")
