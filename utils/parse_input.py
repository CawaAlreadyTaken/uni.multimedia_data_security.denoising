def parse_algorithms_input(input_str):
    """
    Given a string that may contain:
      - single numbers (e.g. '2')
      - multiple comma-separated numbers (e.g. '1,3')
      - "all"
    this function returns a sorted list of integers without duplicates.
    """
    algorithms = set()  # use a set to avoid duplicates

    if input_str == 'all':
        return [1, 2, 3]

    for part in input_str.split(','):
        try:
            num = int(part)
            if 1 <= num <= 3:
                algorithms.add(num)
        except ValueError:
            pass

    return sorted(algorithms)  # return a sorted list of integers

def parse_graphs_input(input_str):
    """
    Given a string that may contain:
      - single numbers (e.g. '2')
      - multiple comma-separated numbers (e.g. '1,4')
      - "all"
    this function returns a sorted list of integers without duplicates.
    """
    out = set()  # use a set to avoid duplicates

    if input_str == 'all':
        return [1, 2, 3, 4, 5]

    for part in input_str.split(','):
        try:
            num = int(part)
            if 1 <= num <= 5:
                out.add(num)
        except ValueError:
            pass

    return sorted(out) 


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
    ordered = sorted(devices)

    # Filter out devices not in [1..35]
    chosen_devices = [n for n in ordered if 1 <= n <= 35]

    return [fill(x) for x in chosen_devices]

def fill(num: int) -> str:
    """
    Given a number, pads it with zeros if it's less than 10.
    """
    if num < 10:
        return f"0{num}"
    return str(num)
