from graphs.generate_confusion_matrix import generate_confusion_matrix
from utils.parse_algorithms_input import parse_algorithms_input
from graphs.generate_histogram import generate_histogram
from utils.parse_device_input import parse_device_input
from graphs.best_worst_metrics import parse_metrics_absolute_value
from graphs.best_worst_metrics import parse_metrics_percentage

def menu():
    """
    Displays a menu to the user, asks which algorithm(s) to compare in plots,
    then asks for which metrics to compare for the chosen algorithm(s).
    then asks for input on which device/devices to apply the algorithm(s) to
    """
    while True:
        print("\n===== GRAPHS MENU =====")

        # Now ask for the devices on which to apply the chosen algorithm(s).
        print("------------------------------------------")
        print()
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

        print("------------------------------------------")
        print()
        graphs_input = input("Consider that (1) = histogram, (2) = confusion matrix, (3) = best_worse results\n"
                                "Enter the graph(s) number(s) between 1 and 2 to generate.\n"
                                "You can specify them in these ways:\n"
                                " - Single graph (e.g. '2')\n" 
                                " - Multiple comma-separated graphs (e.g. '1,2')\n"
                                "Otherwise, you can write:\n"
                                "all) Generate both graphs\n"
                                "q) Quit graphs builder, go back\n"
                                "Your choice: ").strip().lower() 

        if graphs_input == 'q':
            print("Going back.")
            break

        graphs_input = parse_algorithms_input(graphs_input) # This is fine for parsing graphs aswell

        for graph_identifier in graphs_input:
            if graph_identifier == 1:
                print("------------------------------------------")
                print()
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

                algorithms_input = parse_algorithms_input(choice)

                print("Generating histogram graph")
                generate_histogram(algorithms_input, chosen_devices)
            elif graph_identifier == 2:
                print("------------------------------------------")
                print()
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

                algorithms_input = parse_algorithms_input(choice)

                print("Generating confusion matrix graph")
                generate_confusion_matrix(algorithms_input, chosen_devices)

            elif graph_identifier == 3:
                print("------------------------------------------")
                print()
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

                algorithms_input = parse_algorithms_input(choice)

                parse_metrics_absolute_value(algorithms_input, chosen_devices)

            elif graph_identifier == 4:
                print("------------------------------------------")
                print()
                print("Note that this option always considers all methods\n")
                parse_metrics_percentage(chosen_devices)
            else:
                continue

        # Optionally, ask if the user wants to continue or break out
        print("------------------------------------------")
        print()
        cont = input("Do you want to generate more graphs? (y/n): ").strip().lower()
        if cont not in ['y', 'yes']:
            print("Exiting the program.")
            break

if __name__ == "__main__":
    menu()
