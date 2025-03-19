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
