from anonymizer.fingerprint_removal import main as fingerprint_removal
from anonymizer.median_filtering import main as median_filtering
from anonymizer.adp2 import main as adp2

def parse_device_input(input_str):
    """
    Given a string that may contain:
      - single numbers (e.g. '8')
      - multiple comma-separated numbers (e.g. '8,10,12')
      - ranges with a hyphen (e.g. '6-10')
      - or any combination of these (e.g. '5,7-9,12')
    this function returns a sorted list of integers without duplicates.
    """
    devices = set()  # use a set to avoid duplicates

    # Split on commas first
    parts = input_str.split(',')
    for part in parts:
        part = part.strip()
        # Check if this part contains a hyphen for a range
        if '-' in part:
            start_str, end_str = part.split('-')
            start, end = int(start_str.strip()), int(end_str.strip())
            # Add the range of numbers
            for num in range(start, end + 1):
                devices.add(num)
        else:
            # Single device
            devices.add(int(part))

    # Return a sorted list of devices
    return sorted(devices)


def menu():
    """
    Displays a menu to the user, asks which algorithm(s) to run,
    then asks for input on which device/devices to apply the algorithm(s) to.
    """
    while True:
        print("\n===== MENU =====")
        print("1) Fingerprint Removal")
        print("2) Median Filtering")
        print("3) ADP2")
        print("all) Apply all three algorithms")
        print("h or help) Show this menu description again")
        print("q or quit) Exit the program")

        choice = input("Select an option: ").strip().lower()

        if choice in ['q', 'quit']:
            print("Exiting the program.")
            break
        elif choice in ['h', 'help']:
            print("\n--- HELP ---")
            print("Choose '1', '2', or '3' to apply a specific algorithm.")
            print("Choose 'all' to apply all three algorithms.")
            print("Enter 'q' or 'quit' to exit.")
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

        # Filter out devices not in [1..35]
        chosen_devices = [n for n in chosen_devices if 1 <= n <= 35]
        if not chosen_devices:
            print("No valid devices selected (must be between 1 and 35). Try again.")
            continue

        # Apply chosen algorithm(s)
        if choice == '1':
            fingerprint_removal(chosen_devices)
        elif choice == '2':
            median_filtering(chosen_devices)
        elif choice == '3':
            adp2(chosen_devices)
        elif choice == 'all':
            fingerprint_removal(chosen_devices)
            median_filtering(chosen_devices)
            adp2(chosen_devices)

        # Optionally, ask if the user wants to continue or break out
        cont = input("Do you want to process more? (y/n): ").strip().lower()
        if cont not in ['y', 'yes']:
            print("Exiting the program.")
            break


if __name__ == "__main__":
    menu()
