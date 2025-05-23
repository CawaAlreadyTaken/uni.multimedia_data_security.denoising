from utils.constants import BASEPATH, FINGERPRINTSPATH, OUTPUTPATH, OUTPUT_GRAPHS_FOLDER
from pathlib import Path
import numpy as np
import glob
import json 
import sys
import os


def parse_metrics_absolute_value(algorithms, chosen_devices):

    algorithm_mapping = {1: "fingerprint_removal", 2: "median_filtering", 3: "adp2"}

    for algorithm in algorithms:
        # bigger is better
        best_wpsnr = 0.0 
        best_ssim = 0.0 
        best_delta_ccn = 0.0
        best_delta_pce = 0.0

        worst_wpsnr = sys.float_info.max
        worst_ssim =  sys.float_info.max
        worst_delta_ccn = sys.float_info.max
        worst_delta_pce = sys.float_info.max

        print("finding best and worst result for ", algorithm_mapping.get(algorithm))

        for device in chosen_devices:
            print("calc device ", device)
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
                    
                        if metrics[img_name]["initial_pce"]- metrics[img_name]["pce"]>best_delta_pce:
                            best_delta_pce = metrics[img_name]["initial_pce"]- metrics[img_name]["pce"]
                        if metrics[img_name]["initial_pce"]- metrics[img_name]["pce"]<worst_delta_pce:
                            worst_delta_pce = metrics[img_name]["initial_pce"]- metrics[img_name]["pce"]

                        if metrics[img_name]["initial_ccn"]- metrics[img_name]["ccn"]>best_delta_ccn:
                            best_delta_ccn = metrics[img_name]["initial_ccn"]- metrics[img_name]["ccn"]
                        if metrics[img_name]["initial_ccn"]- metrics[img_name]["ccn"]<worst_delta_ccn:
                            worst_delta_ccn = metrics[img_name]["initial_ccn"]- metrics[img_name]["ccn"]

    
                    

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


def parse_metrics_percentage(chosen_devices):
    # always considering all the algorithms
    algorithms = ["fingerprint_removal", "median_filtering", "adp2"]

    best_wpsnr_count=[0,0,0]
    best_ssim_count=[0,0,0]
    best_delta_pce_count=[0,0,0]
    best_delta_ccn_count=[0,0,0]
    total_img = 0 

    path0 = os.path.join(OUTPUTPATH, algorithms[0])
    path1 = os.path.join(OUTPUTPATH, algorithms[1])
    path2 = os.path.join(OUTPUTPATH, algorithms[2])

    for device in chosen_devices:
        path0_device = os.path.join(path0, "D"+str(device).zfill(2))
        path1_device = os.path.join(path1, "D"+str(device).zfill(2))
        path2_device = os.path.join(path2, "D"+str(device).zfill(2))

    try:
        # load files
        with open(os.path.join(path0_device, "metrics.json"), 'r') as f:
            metrics0 = json.load(f)

        with open(os.path.join(path1_device, "metrics.json"), 'r') as f:
            metrics1 = json.load(f)

        with open(os.path.join(path2_device, "metrics.json"), 'r') as f:
            metrics2 = json.load(f)

        # one image folder is needed 
        for fname in sorted(glob.glob(os.path.join(path0_device, "*.jpg"))):
            img_name = str(fname[-18:])
            # print(img_name)
            # print("update")

            if img_name not in metrics0: 
                print(img_name, " not existing in ", algorithms[0])
            elif img_name not in metrics1: 
                print(img_name, " not existing in ", algorithms[1])
            elif img_name not in metrics2: 
                print(img_name, " not existing in ", algorithms[2])
            else:
                total_img += 1
                index_of_max = max(enumerate([metrics0[img_name]["wpsnr"], metrics1[img_name]["wpsnr"], metrics2[img_name]["wpsnr"]]), key=lambda x: x[1])[0]
                best_wpsnr_count[index_of_max] += 1

                index_of_max = max(enumerate([metrics0[img_name]["ssim"], metrics1[img_name]["ssim"], metrics2[img_name]["ssim"]]), key=lambda x: x[1])[0]
                best_ssim_count[index_of_max] += 1


                delta0 = metrics0[img_name]["initial_pce"]- metrics0[img_name]["pce"]
                delta1 = metrics1[img_name]["initial_pce"]- metrics1[img_name]["pce"]
                delta2 = metrics2[img_name]["initial_pce"]- metrics2[img_name]["pce"]
                index_of_max = max(enumerate([delta0, delta1, delta2]), key=lambda x: x[1])[0]
                best_delta_pce_count[index_of_max] += 1

                delta0 = metrics0[img_name]["initial_ccn"]- metrics0[img_name]["ccn"]
                delta1 = metrics1[img_name]["initial_ccn"]- metrics1[img_name]["ccn"]
                delta2 = metrics2[img_name]["initial_ccn"]- metrics2[img_name]["ccn"]
                index_of_max = max(enumerate([delta0, delta1, delta2]), key=lambda x: x[1])[0]
                best_delta_ccn_count[index_of_max] += 1

    except FileNotFoundError:
            print(f"Warning: metric.json not found")
    except json.JSONDecodeError:
            print(f"Warning: Invalid JSON in metric.json")
    except Exception as e:
            print(f"Warning: Error processing : {str(e)}")


    if(total_img==0):
        print("no images and metrics to consider")
    else:
        print("Considering ", total_img, "images\n")
        print("WPSNR: \n\t", algorithms[0], "wins in ", (best_wpsnr_count[0]/total_img)*100, "%\n\t", algorithms[1], "wins in ", (best_wpsnr_count[1]/total_img)*100, "%\n\t", algorithms[2], "wins in ", (best_wpsnr_count[2]/total_img)*100, "%")
        print("SSIM: \n\t", algorithms[0], "wins in ", (best_ssim_count[0]/total_img)*100, "%\n\t", algorithms[1], "wins in ", (best_ssim_count[1]/total_img)*100, "%\n\t", algorithms[2], "wins in ", (best_ssim_count[2]/total_img)*100, "%")
        print("DELTA PCE: \n\t", algorithms[0], "wins in ", (best_delta_pce_count[0]/total_img)*100, "%\n\t", algorithms[1], "wins in ", (best_delta_pce_count[1]/total_img)*100, "%\n\t", algorithms[2], "wins in ", (best_delta_pce_count[2]/total_img)*100, "%")
        print("DELTA CCN: \n\t", algorithms[0], "wins in ", (best_delta_ccn_count[0]/total_img)*100, "%\n\t", algorithms[1], "wins in ", (best_delta_ccn_count[1]/total_img)*100, "%\n\t", algorithms[2], "wins in ", (best_delta_ccn_count[2]/total_img)*100, "%")


