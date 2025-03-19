from prnu_estimation.main import menu as generate_fingerprints
from anonymizer.main import menu as anonymize_images
from graphs.main import menu as generate_graphs
from metrics.main import menu as show_metrics

def print_help():
    """
    This function prints detailed information on how to use the application.
    """
    print("\n=== MAIN HELP ===")
    print("1) Generate fingerprints: Creates unique identifiers for your data or images.")
    print("2) Anonymize images: Removes sensitive information from images.")
    print("3) Show metrics: Displays current metrics/statistics.")
    print("4) Generate graphs: Creates visual representations of data.")
    print("h) Help: Prints this help message.")
    print("q) Quit: Exits the application.\n")


def menu():
    """
    Displays a menu to the user and calls the corresponding function
    based on the user's choice.
    """
    while True:
        print("\n=== MAIN MENU ===")
        print("\nPlease choose an option:")
        print("1) Generate fingerprints")
        print("2) Anonymize images")
        print("3) Show metrics")
        print("4) Generate graphs")
        print("h) Help")
        print("q) Quit")

        choice = input("\nEnter your choice: ").strip().lower()

        if choice == '1':
            generate_fingerprints()
        elif choice == '2':
            anonymize_images()
        elif choice == '3':
            show_metrics()
        elif choice == '4':
            generate_graphs()
        elif choice == 'h':
            print_help()
        elif choice == 'q':
            print("Exiting the program. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    menu()
