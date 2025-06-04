from anonymizer.fingerprint_removal import main as fingerprint_removal
from anonymizer.median_filtering import main as median_filtering
from utils.parse_input import parse_device_input
from anonymizer.apd2 import main as apd2

def menu():
    """
    Displays a menu to the user, asks which algorithm(s) to run,
    then asks for input on which device/devices to apply the algorithm(s) to.
    """
    while True:
        print("\n===== ANONYMIZER MENU =====")
        print("\n1) Fingerprint Removal")
        print("2) Median Filtering")
        print("3) APD2")
        print("all) Apply all three algorithms")
        print("h) Show this menu description again")
        print("q) Quit anonymizer, go back")

        choice = input("Select an option: ").strip().lower()

        if choice == 'q':
            print("Exiting the program.")
            break
        elif choice == 'h':
            print("\n--- ANONYMIZER HELP ---")
            print("Choose '1', '2', or '3' to apply a specific algorithm.")
            print("Choose 'all' to apply all three algorithms.")
            print("Enter 'q' to exit.")
            print("-------------\n")
            continue
        elif choice not in ['1', '2', '3', 'all']:
            print("Invalid choice. Try again or type 'h' for help.")
            continue

        # Now ask for the devices on which to apply the chosen algorithm(s).
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
        if choice == '1':
            fingerprint_removal(chosen_devices)
        elif choice == '2':
            median_filtering(chosen_devices)
        elif choice == '3':
            apd2(chosen_devices)
        elif choice == 'all':
            fingerprint_removal(chosen_devices)
            median_filtering(chosen_devices)
            apd2(chosen_devices)

        # Optionally, ask if the user wants to continue or break out
        cont = input("Do you want to process more? (y/n): ").strip().lower()
        if cont not in ['y', 'yes']:
            print("Exiting the program.")
            break

if __name__ == "__main__":
    menu()
