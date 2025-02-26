def menu():
    """
    Displays a menu to the user, asks which algorithm(s) to compare in plots,
    then asks for which metrics to compare for the chosen algorithm(s).
    then asks for input on which device/devices to apply the algorithm(s) to
    """
    while True:
        print("\n===== GRAPHS MENU =====")
        print("Consider that (1) = Fingerprint Removal, (2) = Median Filtering, (3) = ADP2")
        print("Enter the algorithm number(s) between 1 and 3 to process.\n"
            "You can specify them in these ways:\n"
            " - Single algorithm (e.g. '2')\n"
            " - Multiple comma-separated algorithms (e.g. '1,3')\n"
            "Otherwise, you can write:")
        print("all) Apply all three algorithms")
        print("q) Quit graphs builder, go back")

        choice = input("Select an option: ").strip().lower()

        if choice == 'q':
            print("Going back.")
            break
        else:
            algorithms_input = parse_algorithms_input(choice)
            if algorithms_input is None:
                print("Invalid choice. Try again")
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
