def parse_pr_data(data_string):
    # Initialize an empty dictionary to store the results
    pr_values = {}
    
    # Split the input string into lines
    lines = data_string.strip().split('\n')
    
    # Extract the time from the first line
    execution_time = None
    if lines[0].startswith('Time:'):
        time_line = lines[0]
        execution_time = float(time_line.split(':')[1].split()[0])
    
    # Parse the pr values
    for line in lines:
        if line.startswith('pr('):
            # Extract the index and value
            parts = line.split('=')
            index_str = parts[0].strip()
            index = int(index_str[3:-1])  # Extract the number between 'pr(' and ')'
            value = float(parts[1].strip())
            
            # Store in dictionary
            pr_values[index] = value
    
    return execution_time, pr_values


def get_ranks(pr_values):
    """Convert PR values to ranks (higher PR value = higher rank)"""
    # Create a list of (index, value) pairs
    items = list(pr_values.items())
    
    # Sort by PR value in descending order
    sorted_items = sorted(items, key=lambda x: x[1], reverse=True)
    
    # Create a dictionary mapping index to rank
    ranks = {}
    for rank, (index, _) in enumerate(sorted_items):
        ranks[index] = rank
    
    return ranks

def compute_similarity(pr_values1, pr_values2):
    """
    Compute similarity between two PR value dictionaries.
    Lower sum of rank differences means higher similarity.
    """
    # Get ranks for both dictionaries
    ranks1 = get_ranks(pr_values1)
    ranks2 = get_ranks(pr_values2)
    
    # Find common keys
    common_keys = set(ranks1.keys()) & set(ranks2.keys())
    
    if not common_keys:
        return 0  # No common keys, similarity is zero
    
    # Calculate sum of rank differences
    rank_diff_sum = sum(abs(ranks1[k] - ranks2[k]) for k in common_keys)
    
    # Normalize by the maximum possible difference
    max_diff = len(common_keys) * (len(common_keys) - 1)
    if max_diff == 0:
        return 1  # Only one common key, perfect similarity
    
    # Higher similarity = lower normalized difference
    similarity = 1 - (rank_diff_sum / max_diff)
    
    return similarity


def get_gt(fname = "gt.txt"):
    with open(fname, "r") as f:
        s = f.read()
        time, gt = parse_pr_data(s)
    return gt

if __name__ == "__main__":
    get_gt()