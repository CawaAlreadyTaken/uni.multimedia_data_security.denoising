import glob
from utils.constants import BASEPATH, FINGERPRINTSPATH, OUTPUTPATH, OUTPUT_GRAPHS_FOLDER
from metrics.metrics_calculator import compute_pce
from matplotlib.patches import Patch
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
import numpy as np
import seaborn as sns
import json
import os

def find_best_fingerprint(original_path:str,anonymized_path:str):
    print("Finding best fingerprint for ", anonymized_path)
    max_pce = 0
    best_device = 0
    for device in range(1,36):
        fingerprint = np.load(FINGERPRINTSPATH + 'Fingerprint_D' + str(device).zfill(2) + '.npy').astype(np.float32)
        fingerprint = np.repeat(fingerprint[..., np.newaxis], 3, axis=2)
        print("Calculating pce with fingerprint device ", device)
        pce = compute_pce(original_path,anonymized_path,fingerprint)
        if pce is None:
            continue
        if pce > max_pce:
            max_pce = pce
            best_device = device

    return str(best_device).zfill(2)



def generate_confusion_matrix(algorithms_list, devices_list):
    

    # Mapping from algorithm number to folder name
    algorithm_mapping = {1: "fingerprint_removal", 2: "median_filtering", 3: "adp2"}

    # Ensure the output folder exists
    os.makedirs(OUTPUT_GRAPHS_FOLDER, exist_ok=True)

    # Data structure to store pce for each image, one entity for each algorithm
    data = []

    # ------------------------------------------------------------------------------
    # 1) Calculate confusion matrix for each algorithm
    # ------------------------------------------------------------------------------
    for algo in algorithms_list:
        algo_name = algorithm_mapping.get(algo)
        if algo_name is None:
            continue  # skip unknown algorithm

        data_true = []
        data_predicted = []

        for device in devices_list:
            files = sorted(glob.glob(OUTPUTPATH+algo_name+'/D'+device+'/*.jpg'))

            for file in files:
                original_path = os.path.join(BASEPATH+'D'+device+'/nat/'+os.path.basename(file))
                data_true.append(device)
                data_predicted.append(find_best_fingerprint(original_path,file))
        
        np_true = np.array(data_true)
        np_predicted = np.array(data_predicted)

        cm = confusion_matrix(np_true, np_predicted)

        # Class labels
        class_labels = ['D'+x.__str__() for x in range(1,36)]


        # ------------------------------------------------------------------------------
        # 2) Add legend and tighten layout
        # ------------------------------------------------------------------------------
        plt.figure(figsize=(10,10))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=class_labels, yticklabels=class_labels)
        plt.xlabel("Predicted Label")
        plt.ylabel("Actual Label")
        plt.title("Confusion Matrix "+ algo_name)

        # ------------------------------------------------------------------------------
        # 3) Save figure to file
        # ------------------------------------------------------------------------------
        devices_str = "_".join(devices_list)
        filename = f"confusion_matrix_{algo_name}_{devices_str}.png"
        save_path = os.path.join(OUTPUT_GRAPHS_FOLDER, filename)
        plt.savefig(save_path)
        # plt.close()
        print(f"Saved figure to {save_path}")
