from metrics.metrics_calculator import main as metrics_calculator
from utils.parse_device_input import parse_device_input
from utils.constants import OUTPUTPATH

def menu():
    """
    Displays a menu to the user, asks which algorithm(s) to compute the metrics,
    then asks for input on which device/devices to apply the metrics.
    """
    while True:
        print("\n===== METRICS MENU =====")
        print("\n1) Fingerprint Removal")
        print("2) Median Filtering")
        print("3) ADP2")
        print("all) Apply all three algorithms")
        print("h) Show this menu description again")
        print("q) Quit anonymizer, go back")

        #choice = input("Select an option: ").strip().lower()
        choice = '1'

        if choice == 'q':
            print("Exiting the program.")
            break
        elif choice == 'h':
            print("\n--- METRICS HELP ---")
            print("Choose '1', '2', or '3' to apply a specific algorithm.")
            print("Choose 'all' to apply all three algorithms.")
            print("Enter 'q' to exit.")
            print("-------------\n")
            continue
        elif choice not in ['1', '2', '3', 'all']:
            print("Invalid choice. Try again or type 'h' for help.")
            continue

        # Now ask for the devices on which to apply the chosen algorithm(s).
        # devices_input = input("Enter the device number(s) between 1 and 35 to process.\n"
        #                      "You can specify them in these ways:\n"
        #                      " - Single device (e.g. '8')\n"
        #                      " - Multiple comma-separated devices (e.g. '8,9,10')\n"
        #                      " - A range with a dash (e.g. '6-10')\n"
        #                      "Or any combination (e.g. '5,7,10-12').\n"
        #                      "Your choice: ")
        devices_input = '33'

        chosen_devices = parse_device_input(devices_input)

        if not chosen_devices:
            print("No valid devices selected (must be between 1 and 35). Try again.")
            continue

        # Apply chosen algorithm(s)
        if choice == '1':
            metrics_calculator(chosen_devices, OUTPUTPATH + 'fingerprint_removal')
        elif choice == '2':
            metrics_calculator(chosen_devices, OUTPUTPATH + 'median_filtering')
        elif choice == '3':
            metrics_calculator(chosen_devices, OUTPUTPATH + 'adp2')
        elif choice == 'all':
            metrics_calculator(chosen_devices, OUTPUTPATH + 'fingerprint_removal')
            metrics_calculator(chosen_devices, OUTPUTPATH + 'median_filtering')
            metrics_calculator(chosen_devices, OUTPUTPATH + 'adp2')

        # Optionally, ask if the user wants to continue or break out
        cont = input("Do you want to process more? (y/n): ").strip().lower()
        if cont not in ['y', 'yes']:
            print("Exiting the program.")
            break

if __name__ == "__main__":
    menu()
