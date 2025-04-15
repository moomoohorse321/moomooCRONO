import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Parse the data
df = pd.read_csv('pagerank.csv')
# Round accuracy to 2 decimal places for grouping
df['accuracy_rounded'] = np.round(df['accuracy'], 2)

# Filter points based on error threshold E
E = 0.2
filtered_points = []

for acc, group in df.groupby('accuracy_rounded'):
    min_perf = group['perf'].min()
    acceptable = group[group['perf'] <= (1 + E) * min_perf]
    filtered_points.append(acceptable)

filtered_df = pd.concat(filtered_points)

# Find Pareto optimal points
pareto_points = []
for i, row in filtered_df.iterrows():
    is_dominated = False
    for j, other_row in filtered_df.iterrows():
        if i != j and other_row['accuracy'] >= row['accuracy'] and other_row['perf'] <= row['perf'] and \
           (other_row['accuracy'] > row['accuracy'] or other_row['perf'] < row['perf']):
            is_dominated = True
            break
    if not is_dominated:
        pareto_points.append(row)

pareto_df = pd.DataFrame(pareto_points).sort_values('accuracy')

# Create the plot
plt.figure(figsize=(10, 6))

# Plot all filtered points
plt.scatter(filtered_df['accuracy'], filtered_df['perf'], alpha=0.6, label='Data Points')

# Plot Pareto frontier
plt.scatter(pareto_df['accuracy'], pareto_df['perf'], color='red', s=100, marker='*', label='Pareto Optimal')

# Connect Pareto points with a line
plt.plot(pareto_df['accuracy'], pareto_df['perf'], 'r--', alpha=0.5)

# Set log scale for y-axis (performance)
plt.yscale('log')

# Set labels and title
plt.xlabel('Accuracy')
plt.ylabel('Performance (seconds)')
plt.title('Accuracy-Performance Trade-off')
plt.grid(True, alpha=0.3)
plt.legend()

# Display the plot
plt.tight_layout()
plt.show()

# Optional: save the plot
# plt.savefig('accuracy_performance_tradeoff.png', dpi=300)