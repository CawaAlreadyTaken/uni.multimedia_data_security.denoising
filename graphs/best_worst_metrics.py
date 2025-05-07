from utils.constants import BASEPATH, FINGERPRINTSPATH, OUTPUTPATH, OUTPUT_GRAPHS_FOLDER
from pathlib import Path
import numpy as np
import glob
import json 
import sys
import os



def parse_metrics(algorithms, chosen_devices):

    # bigger is better

    algorithm_mapping = {1: "fingerprint_removal", 2: "median_filtering", 3: "adp2"}

    for algorithm in algorithms:
        best_wpsnr = 0.0 
        best_ssim = 0.0 
        best_delta_ccn = 0.0
        best_delta_pce = 0.0

        worst_wpsnr = sys.float_info.max
        worst_ssim =  sys.float_info.max
        worst_delta_ccn = sys.float_info.max
        worst_delta_pce = sys.float_info.max

        print("finding best and worst result for ", algorithm_mapping.get(algorithm))

        for device in range(1, 36):
            path= os.path.join(OUTPUTPATH, algorithm_mapping.get(algorithm), "D"+str(device).zfill(2))

            try:
                with open(os.path.join(path, "metrics.json"), 'r') as f:
                    metrics = json.load(f)

                    for fname in glob.glob(os.path.join(path, "*.jpg")):
                        img_name = str(fname[-18:])
                        if metrics[img_name]["wpsnr"]>best_wpsnr:
                            best_wpsnr = metrics[img_name]["wpsnr"]
                        if metrics[img_name]["wpsnr"]<worst_wpsnr:
                            worst_wpsnr = metrics[img_name]["wpsnr"]

                        if metrics[img_name]["ssim"]>best_ssim:
                            best_ssim = metrics[img_name]["ssim"]
                        if metrics[img_name]["ssim"]<worst_ssim:
                            worst_ssim = metrics[img_name]["ssim"]
                    
                        if metrics[img_name]["pce"]- metrics[img_name]["initial_pce"]>best_delta_pce:
                            best_delta_pce = metrics[img_name]["pce"]- metrics[img_name]["initial_pce"]
                        if metrics[img_name]["pce"]- metrics[img_name]["initial_pce"]<worst_delta_pce:
                            worst_delta_pce = metrics[img_name]["pce"]- metrics[img_name]["initial_pce"]

                        if metrics[img_name]["ccn"]- metrics[img_name]["initial_ccn"]>best_delta_ccn:
                            best_delta_ccn = metrics[img_name]["ccn"]- metrics[img_name]["initial_ccn"]
                        if metrics[img_name]["ccn"]- metrics[img_name]["initial_ccn"]<worst_delta_ccn:
                            worst_delta_ccn = metrics[img_name]["ccn"]- metrics[img_name]["initial_ccn"]

    
                    

            except FileNotFoundError:
                print(f"Warning: metric.json not found in {path}")
            except json.JSONDecodeError:
                print(f"Warning: Invalid JSON in {path}/metric.json")
            except Exception as e:
                print(f"Warning: Error processing {path}: {str(e)}")
        
        print("best wpsnr: ", best_wpsnr)
        print("best ssim: ", best_ssim)
        print("best delta_pce: ", best_delta_pce)
        print("best delta_ccn: ", best_delta_ccn)
        print("---")
        print("worst wpsnr: ", worst_wpsnr)
        print("worst ssim: ", worst_ssim)
        print("worst delta_pce: ", worst_delta_pce)
        print("worst delta_ccn: ", worst_delta_ccn)
        print("----------------------------------")
