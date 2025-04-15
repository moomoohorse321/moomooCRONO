def dump_data_to_csv(accuracy, perf, config_dict, result_file):
    """
        config is a dict of fields from a string to an int
    """
    import csv
    import os

    # Check if the file exists
    file_exists = os.path.isfile(result_file)
    
    # If file exists, read the header to preserve column order
    if file_exists:
        with open(result_file, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            fieldnames = next(reader)  # Get existing header row
    else:
        # If file doesn't exist, create fieldnames as before
        fieldnames = ['accuracy', 'perf'] + list(config_dict.keys())

    # Open the file in append mode
    with open(result_file, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write the header only if the file didn't exist before
        if not file_exists:
            writer.writeheader()

        # Write the data
        row = {'accuracy': accuracy, 'perf': perf}
        row.update(config_dict)
        writer.writerow(row)


if __name__ == "__main__":
    # Example usage
    config_dict = {'worker_threads': 4, 'SKIP_SYNC': 2, 'LOOP_SKIP':166, 'NUM_ITERATIONS': 1666}
    result_file = 'pagerank.csv'

    dump_data_to_csv(1, 1.2, config_dict, result_file)