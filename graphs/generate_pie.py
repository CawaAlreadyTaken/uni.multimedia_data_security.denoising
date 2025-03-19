from utils.constants import OUTPUTPATH, OUTPUT_GRAPHS_FOLDER
import matplotlib.pyplot as plt
import json
import math
import os

def generate_pie(devices_list, item):
    """
    Generate and save pie charts comparing three algorithms on a chosen metric.
    
    Parameters:
        devices_list (list): List of device strings (e.g. ["01", "08", ...])
        item (int): Metric indicator (1: wpsnr, 2: pce, 3: cnn)
                      For:
                        - 1: best is the highest "wpsnr"
                        - 2: best is the highest (initial_pce - pce)
                        - 3: best is the highest (initial_ccn - ccn)
                        
    For each device, the metrics are loaded from:
        f"{OUTPUTPATH}{algorithm}/D{device}/metrics.json"
    where algorithm is one of:
        "fingerprint_removal", "median_filtering", "adp2"
    
    A win for an algorithm is counted only if its score is strictly higher than the others.
    If multiple algorithms tie, no win is recorded for that image.
    
    The resulting pie charts are saved in OUTPUT_GRAPHS_FOLDER.
    If only one device is provided, a single pie chart is generated;
    if multiple devices are provided, a grid of pie charts is generated.
    """
    
    # Check that item is valid
    if item not in [1, 2, 3]:
        raise ValueError("item must be 1, 2, or 3")
    
    # Map the item to a metric name (for labels and titles)
    metric_name = {1: "wpsnr", 2: "pce", 3: "cnn"}[item]
    
    # List of algorithms to compare
    algorithms = ["fingerprint_removal", "median_filtering", "adp2"]
    
    # Dictionary to store win percentages for each device
    device_results = {}
    
    # Loop over each device
    for device in devices_list:
        algo_data = {}
        # Load metrics.json for each algorithm
        for algo in algorithms:
            file_path = os.path.join(OUTPUTPATH, algo, f"D{device}", "metrics.json")
            if not os.path.exists(file_path):
                print(f"Warning: file {file_path} does not exist. Skipping {algo} for device {device}.")
                algo_data[algo] = {}
                continue
            with open(file_path, "r") as f:
                try:
                    algo_data[algo] = json.load(f)
                except json.JSONDecodeError:
                    print(f"Error reading JSON from {file_path}.")
                    algo_data[algo] = {}
        
        # Identify the common images across all algorithms
        keys_sets = [set(algo_data[algo].keys()) for algo in algorithms if algo_data[algo]]
        if not keys_sets:
            print(f"No data available for device {device}. Skipping.")
            continue
        common_images = set.intersection(*keys_sets)
        if not common_images:
            print(f"No common images found for device {device}. Skipping.")
            continue
        
        # Initialize win counters for each algorithm
        wins = {algo: 0 for algo in algorithms}
        total_images = 0
        
        # Process each image in the common set
        for image in common_images:
            scores = {}
            for algo in algorithms:
                metrics = algo_data[algo].get(image, {})
                # Compute score based on selected metric
                if item == 1:
                    score = metrics.get("wpsnr", None)
                elif item == 2:
                    # For pce: higher (initial_pce - pce) is better
                    initial_pce = metrics.get("initial_pce", None)
                    pce = metrics.get("pce", None)
                    score = (initial_pce - pce) if (initial_pce is not None and pce is not None) else None
                elif item == 3:
                    # For cnn: higher (initial_ccn - ccn) is better
                    initial_ccn = metrics.get("initial_ccn", None)
                    ccn = metrics.get("ccn", None)
                    score = (initial_ccn - ccn) if (initial_ccn is not None and ccn is not None) else None
                scores[algo] = score
            
            # Skip the image if any score is missing
            if any(score is None for score in scores.values()):
                continue
            
            # Determine which algorithm has the highest score
            max_score = max(scores.values())
            best_algos = [algo for algo, score in scores.items() if score == max_score]
            # Count as a win only if there is a unique best algorithm
            if len(best_algos) == 1:
                wins[best_algos[0]] += 1
            total_images += 1
        
        if total_images == 0:
            print(f"No valid images for device {device}. Skipping.")
            continue
        
        # Compute the percentage of wins for each algorithm
        percentages = {algo: (wins[algo] / total_images) * 100 for algo in algorithms}
        device_results[device] = percentages
    
    # Check if there is any valid device data to plot
    if not device_results:
        print("No devices with valid data to plot.")
        return
    
    # Ensure the output folder exists
    os.makedirs(OUTPUT_GRAPHS_FOLDER, exist_ok=True)
    
    # Generate the pie charts
    num_devices = len(device_results)
    if num_devices == 1:
        # Single device: one pie chart
        device = list(device_results.keys())[0]
        perc = device_results[device]
        labels = list(perc.keys())
        sizes = [perc[algo] for algo in labels]
        
        plt.figure()
        plt.pie(sizes, labels=labels, autopct='%1.1f%%')
        plt.title(f"Device D{device} - Best Algorithm by {metric_name}")
        output_file = os.path.join(OUTPUT_GRAPHS_FOLDER, f"pie_chart_D{device}_{metric_name}.png")
        plt.savefig(output_file)
        plt.close()
        print(f"Saved pie chart for device D{device} to {output_file}")
        
    else:
        # Multiple devices: arrange subplots in a grid
        n_devices = num_devices
        ncols = math.ceil(math.sqrt(n_devices))
        nrows = math.ceil(n_devices / ncols)
        fig, axes = plt.subplots(nrows, ncols, figsize=(5*ncols, 5*nrows))
        
        # Flatten the axes array for easier iteration
        if n_devices == 1:
            axes = [axes]
        else:
            axes = axes.flatten()
        
        # Turn off any unused axes
        for ax in axes[n_devices:]:
            ax.axis('off')
        
        # Plot a pie chart for each device
        for i, (device, perc) in enumerate(device_results.items()):
            labels = list(perc.keys())
            sizes = [perc[algo] for algo in labels]
            axes[i].pie(sizes, labels=labels, autopct='%1.1f%%')
            axes[i].set_title(f"Device D{device}")
        
        fig.suptitle(f"Best Algorithm by {metric_name} Comparison", fontsize=16)
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        output_file = os.path.join(OUTPUT_GRAPHS_FOLDER, f"pie_chart_multiple_{metric_name}.png")
        plt.savefig(output_file)
        plt.close()
        print(f"Saved pie chart for multiple devices to {output_file}")
