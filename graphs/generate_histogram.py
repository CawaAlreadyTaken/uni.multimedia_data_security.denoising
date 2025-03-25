from utils.constants import OUTPUTPATH, OUTPUT_GRAPHS_FOLDER
from matplotlib.patches import Patch
import matplotlib.pyplot as plt
import numpy as np
import json
import os

def generate_histogram(algorithms_list, devices_list):
    """
    Generates and saves four separate histograms (vertically stacked subplots) using matplotlib:
      - Top: wpsnr
      - Second: ssim
      - Third: (initial_pce - pce)
      - Bottom: (initial_ccn - ccn)
    
    Parameters:
        algorithms_list (list): List of algorithm identifiers (1, 2, or 3).
            Mapping: 1 -> "fingerprint_removal", 2 -> "median_filtering", 3 -> "adp2".
        devices_list (list): List of device strings ("01" to "35").
        
    The metrics are read from files with path:
        f"{OUTPUTPATH}{algorithm_name}/D{device}/metrics.json"
    Each metrics.json file is structured as:
    
        {
            "D04_I_nat_0001.jpg": {
                "wpsnr": ...,
                "ssim": ...,
                "initial_pce": ...,
                "pce": ...,
                "initial_ccn": ...,
                "ccn": ...
            },
            "D04_I_nat_0002.jpg": { ... },
            ...
        }
        
    If only one device is provided, the x-axis represents each image.
    When multiple algorithms are given, the bars for each image are grouped side by side.
    Similarly, if more than one device is provided, the data is averaged over all images per device
    and the x-axis shows the devices.

    The histogram is saved in the folder OUTPUT_GRAPHS_FOLDER.
    """

    # Mapping from algorithm number to folder name
    algorithm_mapping = {1: "fingerprint_removal", 2: "median_filtering", 3: "adp2"}

    # Ensure the output folder exists
    os.makedirs(OUTPUT_GRAPHS_FOLDER, exist_ok=True)

    # Data structure to store metrics
    data = {}

    # ------------------------------------------------------------------------------
    # 1) Load and process data
    # ------------------------------------------------------------------------------
    for algo in algorithms_list:
        algo_name = algorithm_mapping.get(algo)
        if algo_name is None:
            continue  # skip unknown algorithm
        data[algo_name] = {}
        for device in devices_list:
            # Build the file path. Example: "output/fingerprint_removal/D08/metrics.json"
            file_path = os.path.join(OUTPUTPATH, algo_name, f"D{device}", "metrics.json")
            if not os.path.exists(file_path):
                print(f"Warning: File {file_path} not found.")
                continue
            with open(file_path, "r") as f:
                metrics = json.load(f)
            
            if len(devices_list) == 1:
                # For a single device, store per-image values.
                for image_name, values in metrics.items():
                    wpsnr = values.get("wpsnr", 0)
                    ssim = values.get("ssim", 0)
                    diff_pce = max(values.get("initial_pce", 0) - values.get("pce", 0), 0)
                    diff_ccn = max(values.get("initial_ccn", 0) - values.get("ccn", 0), 0)
                    data[algo_name][image_name] = (wpsnr, ssim, diff_pce, diff_ccn)
            else:
                # For multiple devices, compute the average over all images for this device.
                wpsnr_vals = []
                ssim_vals = []
                diff_pce_vals = []
                diff_ccn_vals = []
                for image_name, values in metrics.items():
                    wpsnr_vals.append(values.get("wpsnr", 0))
                    ssim_vals.append(values.get("ssim", 0))
                    diff_pce_vals.append(max(values.get("initial_pce", 0) - values.get("pce", 0), 0))
                    diff_ccn_vals.append(max(values.get("initial_ccn", 0) - values.get("ccn", 0), 0))
                if len(wpsnr_vals) > 0:
                    avg_wpsnr = np.mean(wpsnr_vals)
                    avg_ssim = np.mean(ssim_vals)
                    avg_diff_pce = np.mean(diff_pce_vals)
                    avg_diff_ccn = np.mean(diff_ccn_vals)
                else:
                    avg_wpsnr = avg_ssim = avg_diff_pce = avg_diff_ccn = 0
                data[algo_name][device] = (avg_wpsnr, avg_ssim, avg_diff_pce, avg_diff_ccn)

    # ------------------------------------------------------------------------------
    # 2) Prepare figure with 4 vertical subplots (wpsnr, ssim, pce_diff, ccn_diff)
    # ------------------------------------------------------------------------------
    fig, (ax_wpsnr, ax_ssim, ax_pce, ax_ccn) = plt.subplots(4, 1, figsize=(10, 12), sharex=True)

    # ------------------------------------------------------------------------------
    # 3) Distinguish between single-device (x-axis = images) or multi-device (x-axis = devices)
    # ------------------------------------------------------------------------------
    num_algos = len(algorithms_list)
    algorithm_names = list(data.keys())  # e.g. ["fingerprint_removal", "median_filtering", ...]

    default_colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    
    if len(devices_list) == 1:
        # Single device -> x-axis are image names
        image_names = set()
        for algo_name, values in data.items():
            image_names.update(values.keys())
        image_names = sorted(list(image_names))
        x = np.arange(len(image_names))
        
        width = 0.8 / num_algos if num_algos > 0 else 0.8
        offsets = np.linspace(-width*(num_algos-1)/2, width*(num_algos-1)/2, num_algos)
        
        legend_patches = []

        for i, algo_name in enumerate(algorithm_names):
            wpsnr_values = [data[algo_name].get(img, (0, 0, 0, 0))[0] for img in image_names]
            ssim_values  = [data[algo_name].get(img, (0, 0, 0, 0))[1] for img in image_names]
            pce_values   = [data[algo_name].get(img, (0, 0, 0, 0))[2] for img in image_names]
            ccn_values   = [data[algo_name].get(img, (0, 0, 0, 0))[3] for img in image_names]

            positions = x + offsets[i]
            color = default_colors[i % len(default_colors)]

            ax_wpsnr.bar(positions, wpsnr_values, width=width, color=color)
            ax_ssim.bar(positions, ssim_values, width=width, color=color)
            ax_pce.bar(positions, pce_values, width=width, color=color)
            ax_ccn.bar(positions, ccn_values, width=width, color=color)

            legend_patches.append(Patch(facecolor=color, label=algo_name))
        
        ax_wpsnr.set_ylabel("WPSNR")
        ax_ssim.set_ylabel("SSIM")
        ax_pce.set_ylabel("Initial_PCE - PCE")
        ax_ccn.set_ylabel("Initial_CCN - CCN")
        
        if len(image_names) > 10:
            step = max(1, len(image_names) // 10)  # show at most ~10 labels
            ax_ccn.set_xticks(x[::step])
            ax_ccn.set_xticklabels([image_names[i] for i in range(0, len(image_names), step)],
                                   rotation=45, ha="right")
        else:
            ax_ccn.set_xticks(x)
            ax_ccn.set_xticklabels(image_names, rotation=45, ha="right")
        
        fig.suptitle(f"Metrics for Device D{devices_list[0]}")

    else:
        # Multiple devices -> x-axis are device IDs
        devices_sorted = sorted(devices_list)
        x = np.arange(len(devices_sorted))
        
        width = 0.8 / num_algos if num_algos > 0 else 0.8
        offsets = np.linspace(-width*(num_algos-1)/2, width*(num_algos-1)/2, num_algos)
        
        legend_patches = []

        for i, algo_name in enumerate(algorithm_names):
            wpsnr_values = [data[algo_name].get(dev, (0, 0, 0, 0))[0] for dev in devices_sorted]
            ssim_values  = [data[algo_name].get(dev, (0, 0, 0, 0))[1] for dev in devices_sorted]
            pce_values   = [data[algo_name].get(dev, (0, 0, 0, 0))[2] for dev in devices_sorted]
            ccn_values   = [data[algo_name].get(dev, (0, 0, 0, 0))[3] for dev in devices_sorted]

            positions = x + offsets[i]
            color = default_colors[i % len(default_colors)]
            
            ax_wpsnr.bar(positions, wpsnr_values, width=width, color=color)
            ax_ssim.bar(positions, ssim_values, width=width, color=color)
            ax_pce.bar(positions, pce_values, width=width, color=color)
            ax_ccn.bar(positions, ccn_values, width=width, color=color)

            legend_patches.append(Patch(facecolor=color, label=algo_name))
        
        ax_wpsnr.set_ylabel("WPSNR")
        ax_ssim.set_ylabel("SSIM")
        ax_pce.set_ylabel("Initial_PCE - PCE")
        ax_ccn.set_ylabel("Initial_CCN - CCN")

        ax_ccn.set_xticks(x)
        ax_ccn.set_xticklabels([f"D{dev}" for dev in devices_sorted])

        fig.suptitle("Metrics per Device")
    
    # ------------------------------------------------------------------------------
    # 4) Add legend and tighten layout
    # ------------------------------------------------------------------------------
    ax_wpsnr.legend(handles=legend_patches, title="Algorithms", loc="upper right")
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])

    # ------------------------------------------------------------------------------
    # 5) Save figure to file
    # ------------------------------------------------------------------------------
    algo_names_str = "_".join([algorithm_mapping.get(a, str(a)) for a in algorithms_list])
    devices_str = "_".join(devices_list)
    filename = f"histogram_{algo_names_str}_{devices_str}.png"
    save_path = os.path.join(OUTPUT_GRAPHS_FOLDER, filename)
    plt.savefig(save_path)
    plt.close()
    print(f"Saved figure to {save_path}")
