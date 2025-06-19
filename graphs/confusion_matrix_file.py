import os
import json
import re
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
from utils.constants import BASEPATH, FINGERPRINTSPATH_EVALUATION, OUTPUTPATH, OUTPUT_GRAPHS_FOLDER


def generate_matrix_file(devices, algorithms):

    algorithm_mapping = {1: "fingerprint_removal", 2: "median_filtering", 3: "apd2"}

    for algo in algorithms:
        algorithm = algorithm_mapping.get(algo)

        true_labels = []
        predicted_labels = []

        for device in devices: 
            filepath = os.path.join(OUTPUTPATH, algorithm, "D"+device, "matrix.json")
            try:
                file =open(filepath, 'r')
                data = json.load(file)
            except:
                print("Skipping invalid JSON")
                continue

            for image_name, pce_dict in data.items():
                true_device = int(device)

                # Determine predicted device (device with max PCE)
                max_pce_key = max(pce_dict, key=pce_dict.get)
                predicted_device = int(max_pce_key)

                true_labels.append(true_device)
                predicted_labels.append(predicted_device)
        
        numeric_labels = sorted(set(true_labels + predicted_labels))


        str_labels = [f"D{int(l):02d}" for l in numeric_labels]

        # Generate confusion matrix
        cm = confusion_matrix(true_labels, predicted_labels, labels=numeric_labels)


        # labels = sorted(set(true_labels + predicted_labels))
        # cm = confusion_matrix(true_labels, predicted_labels, labels=labels)

        # Plot confusion matrix
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', xticklabels=str_labels, yticklabels=str_labels, cmap="Blues")
        plt.xlabel("Predicted Device")
        plt.ylabel("True Device")
        plt.title("Device Identification Confusion Matrix")

        # Save confusion matrix image
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_GRAPHS_FOLDER+algorithm+"confusion_matrix.jpg"))
        plt.close()

        print("Confusion matrix saved as 'confusion_matrix.png'")


    # # Walk through all directories and files recursively
    # for dirpath, _, filenames in os.walk(root_dir):
    #     for filename in filenames:
    #         if filename.endswith(".json"):
    #             filepath = os.path.join(dirpath, filename)
    #             with open(filepath, 'r') as file:
    #                 try:
    #                     data = json.load(file)
    #                 except json.JSONDecodeError:
    #                     print(f"Skipping invalid JSON: {filepath}")
    #                     continue

    #                 for image_name, pce_dict in data.items():
    #                     # Extract true device number from image filename
    #                     match = device_pattern.match(image_name)
    #                     if not match:
    #                         continue
    #                     true_device = int(match.group(1))

    #                     # Determine predicted device (device with max PCE)
    #                     max_pce_key = max(pce_dict, key=pce_dict.get)
    #                     predicted_device = int(max_pce_key)

    #                     true_labels.append(true_device)
    #                     predicted_labels.append(predicted_device)

    # # Create confusion matrix
    # labels = sorted(set(true_labels + predicted_labels))
    # cm = confusion_matrix(true_labels, predicted_labels, labels=labels)

    # # Plot confusion matrix
    # plt.figure(figsize=(10, 8))
    # sns.heatmap(cm, annot=True, fmt='d', xticklabels=labels, yticklabels=labels, cmap="Blues")
    # plt.xlabel("Predicted Device")
    # plt.ylabel("True Device")
    # plt.title("Device Identification Confusion Matrix")

    # # Save confusion matrix image
    # plt.tight_layout()
    # plt.savefig("confusion_matrix.png")
    # plt.close()

    # print("Confusion matrix saved as 'confusion_matrix.png'")
