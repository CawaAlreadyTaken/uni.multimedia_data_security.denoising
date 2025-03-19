from utils.constants import OUTPUTPATH, OUTPUT_GRAPHS_FOLDER
from matplotlib.patches import Patch
import matplotlib.pyplot as plt
import numpy as np
import json
import os

def generate_histogram(algorithms_list, devices_list):
    """
    Generates and saves a stacked histogram using matplotlib.
    
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
    For each bar (or bar group) the stacked segments are:
        - bottom: wpsnr,
        - middle: (initial_pce - pce),
        - top: (initial_ccn - ccn).
        
    If more than one device is provided, the data is averaged over all images per device.
    
    The histogram is saved in the folder OUTPUT_GRAPHS_FOLDER.
    """
    # Mapping from algorithm number to folder name
    algorithm_mapping = {1: "fingerprint_removal", 2: "median_filtering", 3: "adp2"}
    
    # Define the input and output paths (adjust these as needed)
    os.makedirs(OUTPUT_GRAPHS_FOLDER, exist_ok=True)
    
    # Data structure to store metrics.
    # If only one device is provided:
    #    data[algorithm_name] = { image_name: (wpsnr, diff_pce, diff_ccn), ... }
    # Otherwise (multiple devices):
    #    data[algorithm_name] = { device: (avg_wpsnr, avg_diff_pce, avg_diff_ccn), ... }
    data = {}
    
    # Loop over each algorithm and device to load the metrics.
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
                # (In this case, data[algo_name] will map image_name -> (wpsnr, diff_pce, diff_ccn))
                for image_name, values in metrics.items():
                    wpsnr = values.get("wpsnr", 0)
                    diff_pce = max(values.get("initial_pce", 0) - values.get("pce", 0), 0)
                    diff_ccn = max(values.get("initial_ccn", 0) - values.get("ccn", 0), 0)
                    data[algo_name][image_name] = (wpsnr, diff_pce, diff_ccn)
            else:
                # For multiple devices, compute the average over all images for this device.
                wpsnr_vals = []
                diff_pce_vals = []
                diff_ccn_vals = []
                for image_name, values in metrics.items():
                    wpsnr_vals.append(values.get("wpsnr", 0))
                    diff_pce_vals.append(max(values.get("initial_pce", 0) - values.get("pce", 0), 0))
                    diff_ccn_vals.append(max(values.get("initial_ccn", 0) - values.get("ccn", 0), 0))
                if len(wpsnr_vals) > 0:
                    avg_wpsnr = np.mean(wpsnr_vals)
                    avg_diff_pce = np.mean(diff_pce_vals)
                    avg_diff_ccn = np.mean(diff_ccn_vals)
                else:
                    avg_wpsnr = avg_diff_pce = avg_diff_ccn = 0
                data[algo_name][device] = (avg_wpsnr, avg_diff_pce, avg_diff_ccn)
    
    # Set up default colors for the three metric segments (using default cycle colors).
    default_colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    color_wpsnr = default_colors[0]
    color_diff_pce = default_colors[1]
    color_diff_ccn = default_colors[2]
    
    # Define hatch patterns to differentiate algorithms if more than one is provided.
    hatch_patterns = ["", "//", "xx", "o", "O", ".", "*"]
    num_algos = len(algorithms_list)
    hatches = hatch_patterns[:num_algos]
    
    plt.figure(figsize=(10, 6))
    
    ax = plt.gca()
    
    if len(devices_list) == 1:
        # Single device: x-axis are images.
        # Collect all image names from all algorithms (assume they are similar)
        image_names = set()
        for algo_name, values in data.items():
            image_names.update(values.keys())
        image_names = sorted(list(image_names))
        x = np.arange(len(image_names))
        
        # Define bar width and offsets for grouping (if multiple algorithms)
        width = 0.8 / num_algos if num_algos > 0 else 0.8
        offsets = np.linspace(-width*(num_algos-1)/2, width*(num_algos-1)/2, num_algos)
        
        # Plot bars for each algorithm
        for i, algo_name in enumerate(data.keys()):
            # Extract metric values for each image (default to 0 if missing)
            wpsnr_heights = [data[algo_name].get(img, (0, 0, 0))[0] for img in image_names]
            diff_pce_heights = [data[algo_name].get(img, (0, 0, 0))[1] for img in image_names]
            diff_ccn_heights = [data[algo_name].get(img, (0, 0, 0))[2] for img in image_names]
            
            positions = x + offsets[i]
            # Plot the stacked bar: bottom segment (wpsnr)
            bar1 = ax.bar(positions, wpsnr_heights, width=width, color=color_wpsnr, hatch=hatches[i])
            # Middle segment: (initial_pce - pce)
            bar2 = ax.bar(positions, diff_pce_heights, width=width, bottom=wpsnr_heights, 
                          color=color_diff_pce, hatch=hatches[i])
            # Top segment: (initial_ccn - ccn)
            bottoms = [a + b for a, b in zip(wpsnr_heights, diff_pce_heights)]
            bar3 = ax.bar(positions, diff_ccn_heights, width=width, bottom=bottoms, 
                          color=color_diff_ccn, hatch=hatches[i])
        
        ax.set_xlabel("Images")
        ax.set_ylabel("Metric Values")
        ax.set_title(f"Metrics Histogram for Device D{devices_list[0]}")
        if len(image_names) > 10:
            step = max(1, len(image_names) // 10)  # show at most 10 labels
            ax.set_xticks(x[::step])
            ax.set_xticklabels([image_names[i] for i in range(0, len(image_names), step)], rotation=45, ha="right")
        else:
            ax.set_xticks(x)
            ax.set_xticklabels(image_names, rotation=45, ha="right")
        
    else:
        # Multiple devices: x-axis are devices.
        devices_sorted = sorted(devices_list)
        x = np.arange(len(devices_sorted))
        width = 0.8 / num_algos if num_algos > 0 else 0.8
        offsets = np.linspace(-width*(num_algos-1)/2, width*(num_algos-1)/2, num_algos)
        
        for i, algo_name in enumerate(data.keys()):
            # Extract average values per device (default to 0 if missing)
            wpsnr_heights = [data[algo_name].get(device, (0, 0, 0))[0] for device in devices_sorted]
            diff_pce_heights = [data[algo_name].get(device, (0, 0, 0))[1] for device in devices_sorted]
            diff_ccn_heights = [data[algo_name].get(device, (0, 0, 0))[2] for device in devices_sorted]
            
            positions = x + offsets[i]
            bar1 = ax.bar(positions, wpsnr_heights, width=width, color=color_wpsnr, hatch=hatches[i])
            bar2 = ax.bar(positions, diff_pce_heights, width=width, bottom=wpsnr_heights,
                          color=color_diff_pce, hatch=hatches[i])
            bottoms = [a + b for a, b in zip(wpsnr_heights, diff_pce_heights)]
            bar3 = ax.bar(positions, diff_ccn_heights, width=width, bottom=bottoms,
                          color=color_diff_ccn, hatch=hatches[i])
        
        ax.set_xlabel("Devices")
        ax.set_ylabel("Metric Values")
        ax.set_title("Metrics Histogram per Device")
        ax.set_xticks(x)
        ax.set_xticklabels([f"D{device}" for device in devices_sorted])
    
    plt.tight_layout()
    
    # Create legends.
    # Legend for the metric segments (consistent across all bars)
    metric_handles = [
        Patch(facecolor=color_wpsnr, label="wpsnr"),
        Patch(facecolor=color_diff_pce, label="(pce - initial_pce)"),
        Patch(facecolor=color_diff_ccn, label="(ccn - initial_ccn)")
    ]
    # If more than one algorithm, add an extra legend to indicate the algorithm grouping (via hatch patterns)
    if num_algos > 1:
        algo_handles = []
        # Ensure we list algorithms in the same order as provided
        for i, algo in enumerate([algorithm_mapping.get(a) for a in algorithms_list]):
            # Here we use a patch with the same hatch; the facecolor is set to the wpsnr color as a proxy.
            algo_handles.append(Patch(facecolor=color_wpsnr, hatch=hatches[i], label=algo))
        leg1 = ax.legend(handles=algo_handles, title="Algorithms", loc="upper left")
        leg2 = ax.legend(handles=metric_handles, title="Metrics", loc="upper right")
        ax.add_artist(leg1)  # add the algorithm legend back
    else:
        ax.legend(handles=metric_handles, title="Metrics")
    
    # Save the figure.
    # Build a filename based on the selected algorithms and devices.
    algo_names_str = "_".join([algorithm_mapping.get(a, str(a)) for a in algorithms_list])
    devices_str = "_".join(devices_list)
    filename = f"histogram_{algo_names_str}_{devices_str}.png"
    save_path = os.path.join(OUTPUT_GRAPHS_FOLDER, filename)
    plt.savefig(save_path)
    plt.close()
