from utils.constants import BASEPATH, FINGERPRINTSPATH_EVALUATION, OUTPUTPATH, OUTPUT_GRAPHS_FOLDER
from metrics.metrics_calculator import compute_pce
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import concurrent.futures
import seaborn as sns
import numpy as np
import json
import glob
import os

def find_best_fingerprint(original_path: str, anonymized_path: str):
    print("Finding best fingerprint for", anonymized_path)
    max_pce = 0
    best_device = 0
    result = {}
    for d in range(1, 36):
        fingerprint_file = os.path.join(FINGERPRINTSPATH_EVALUATION, f'Fingerprint_D{str(d).zfill(2)}.npy')
        if not os.path.exists(fingerprint_file):
            print(f"Warning: File {fingerprint_file} not found.")
            continue
        fingerprint = np.load(fingerprint_file).astype(np.float32)
        fingerprint = np.repeat(fingerprint[..., np.newaxis], 3, axis=2)
        print("Calculating pce with fingerprint device", d)
        pce = compute_pce(original_path, anonymized_path, fingerprint)
        if pce is None:
            continue
        result[d] = pce
        if pce > max_pce:
            max_pce = pce
            best_device = d

    return str(best_device).zfill(2), result

def process_file(args):
    original_path, anonymized_path, device = args
    file = os.path.basename(anonymized_path)
    best_device, pce_dict = find_best_fingerprint(original_path, anonymized_path)

    # Determina il nome dell’algoritmo dalla struttura del path
    algo_name = anonymized_path.split(os.sep)[-3]  # es: output/ALGO_NAME/Dxx/file.jpg

    # Path al JSON
    matrix_json_path = os.path.join(OUTPUTPATH, algo_name, f"D{device}", "matrix.json")

    # Carica il file se esiste
    if os.path.exists(matrix_json_path):
        with open(matrix_json_path, "r") as f:
            matrix_data = json.load(f)
    else:
        matrix_data = {}

    # Salva solo il PCE relativo al best device trovato
    matrix_data[file] = {str(k): v for k, v in pce_dict.items()}

    # Scrivi nel JSON
    with open(matrix_json_path, "w") as f:
        json.dump(matrix_data, f, indent=4)

    return device, best_device, file, pce_dict.get(int(best_device), None)

def generate_confusion_matrix(algorithms_list, devices_list):
    # Mapping from algorithm number to folder name
    algorithm_mapping = {1: "fingerprint_removal", 2: "median_filtering", 3: "apd2"}

    # Ensure the output folder exists
    os.makedirs(OUTPUT_GRAPHS_FOLDER, exist_ok=True)

    # ------------------------------------------------------------------------------
    # 1) Calculate confusion matrix for each algorithm
    # ------------------------------------------------------------------------------
    for algo in algorithms_list:
        algo_name = algorithm_mapping.get(algo)
        if algo_name is None:
            continue  # skip unknown algorithm

        data_true = []
        data_predicted = []
        tasks = []

        # Loop through each device and each file in the algorithm's folder
        for device in devices_list:
            folder_path = os.path.join(OUTPUTPATH, algo_name, 'D' + device)
            files = sorted(glob.glob(os.path.join(folder_path, '*.jpg')))

            # Build the metrics file path. Example: "output/fingerprint_removal/D08/metrics.json"
            metrics_path = os.path.join(OUTPUTPATH, algo_name, f"D{device}", "metrics.json")
            if not os.path.exists(metrics_path):
                print(f"Warning: File {metrics_path} not found.")
                exit(1)
            with open(metrics_path, "r") as f:
                metrics_info = json.load(f)

            for file in files:
                final_image_pce = metrics_info.get(os.path.basename(file)).get("pce")
                initial_image_pce = metrics_info.get(os.path.basename(file)).get("initial_pce")
                # New: skip image if not anonymized
                if final_image_pce > 50 or (initial_image_pce < final_image_pce):
                    continue
                # Construct the path to the original image
                original_path = os.path.join(BASEPATH, 'D' + device, 'nat', os.path.basename(file))
                tasks.append((original_path, file, device))
                # tasks.append((original_path, original_path, device))

        # ------------------------------------------------------------------------------
        # 2) Use ProcessPoolExecutor to parallelize the computation
        # ------------------------------------------------------------------------------
        with concurrent.futures.ProcessPoolExecutor(max_workers=6) as executor:
            results = list(executor.map(process_file, tasks))

        # Collect results from parallel execution
        for device, best_device, file, pce in results:
            data_true.append(device)
            data_predicted.append(best_device)

        np_true = np.array(data_true)
        np_predicted = np.array(data_predicted)

        # Compute confusion matrix using sklearn
        cm = confusion_matrix(np_true, np_predicted)
        print(np_true)
        print()
        print(np_predicted)
        print()
        print(cm)

        # Class labels for devices (D1, D2, ..., D35)
        class_labels = ['D' + str(x) for x in range(1, 36)]

        # ------------------------------------------------------------------------------
        # 3) Plot confusion matrix using seaborn
        # ------------------------------------------------------------------------------
        plt.figure(figsize=(10, 10))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=class_labels, yticklabels=class_labels)
        plt.xlabel("Predicted Label")
        plt.ylabel("Actual Label")
        plt.title("Confusion Matrix " + algo_name)

        # ------------------------------------------------------------------------------
        # 4) Save the figure to file
        # ------------------------------------------------------------------------------
        devices_str = "_".join(devices_list)
        filename = f"confusion_matrix_{algo_name}_{devices_str}.png"
        save_path = os.path.join(OUTPUT_GRAPHS_FOLDER, filename)
        plt.savefig(save_path)
        plt.close()
        print(f"Saved figure to {save_path}")
