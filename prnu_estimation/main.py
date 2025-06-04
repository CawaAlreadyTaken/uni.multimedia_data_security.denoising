from utils.to_remove import parse_device_input
from utils.extraction import extract_multiple_aligned
from utils.rotate_image import rotate_image
from multiprocessing import cpu_count
from utils.constants import BASEPATH
from scipy.io import savemat
import numpy as np
import glob
import cv2

def estimate(devices_list: list[str]):

    devices = sorted(glob.glob(BASEPATH+'D*'))

    for device_path in devices:
        if device_path[-2:] not in devices_list:
            continue
        files = sorted(glob.glob(device_path + '/flat/*.*'))
        K_k = []
        imgs = []
        group_size = 30
        idx_1 = 0
        idx_2 = 0
        for img_name in files:
            print(f"[ESTIMATING FINGERPRINT] {img_name}")
            img = cv2.imread(img_name)
            try:
                img = rotate_image(img, img_name)

                imgs += [img.astype(dtype=np.uint8)]
                
            except:
                if np.shape(img)[0]<np.shape(img)[1]:
                    imgs += [img.astype(dtype=np.uint8)]

        if not len(imgs):
            for img_name in files:
                img = cv2.imread(img_name)
                if np.shape(img)[0]<np.shape(img)[1]:
                    imgs += [img.astype(dtype=np.uint8)]
        
        if not len(imgs):
            print('No images found for device', device_path[-3:])
            continue
        print('compute fingerprint', device_path[-3:], ' with: ', len(imgs), 'IMAGES')
        K_k += [extract_multiple_aligned(imgs, processes=cpu_count(), sigma=3)]
        K_k = np.stack(K_k, 0)

        del imgs
        K = np.squeeze(K_k, axis=0)
        out_name = 'fingerprints/Fingerprint_' + device_path[-3:] + '.npy'
        np.save(out_name, K)

def menu():
    """
    Displays a menu to the user, asks on which device/devices
    to estimate the prnu fingerprints.
    """
    while True:
        print("\n===== ESTIMATOR MENU =====")
        print("\n1) Estimate fingerprints")
        print("h) Show this menu description again")
        print("q) Quit estimator, go back")

        choice = input("Select an option: ").strip().lower()

        if choice == 'q':
            print("Exiting the program.")
            break
        elif choice == 'h':
            print("\n--- ESTIMATOR HELP ---")
            print("Write '1' to estimate the fingerprints.")
            print("Choose 'all' to apply all three algorithms.")
            print("Enter 'q' to exit.")
            print("-------------\n")
            continue
        elif choice != '1':
            print("Invalid choice. Try again or type 'h' for help.")
            continue

        # Now ask for the devices on which to estimate the fingerprints.
        devices_input = input("Enter the device number(s) between 1 and 35 to process.\n"
                             "You can specify them in these ways:\n"
                             " - Single device (e.g. '8')\n"
                             " - Multiple comma-separated devices (e.g. '8,9,10')\n"
                             " - A range with a dash (e.g. '6-10')\n"
                             "Or any combination (e.g. '5,7,10-12').\n"
                             "Your choice: ")

        chosen_devices = parse_device_input(devices_input)

        if not chosen_devices:
            print("No valid devices selected (must be between 1 and 35). Try again.")
            continue

        # Apply chosen algorithm(s)
        estimate(chosen_devices)

        # Optionally, ask if the user wants to continue or break out
        cont = input("Do you want to process more? (y/n): ").strip().lower()
        if cont not in ['y', 'yes']:
            print("Quitting estimator, going back.")
            break

if __name__ == "__main__":
    menu()
