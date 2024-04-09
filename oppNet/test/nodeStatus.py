import matplotlib.pyplot as plt

# Dummy data
nodes = [9, 12, 15, 18, 21, 24, 27, 30, 33, 36]
time_taken_without_smart_contract = [2.6, 3.4, 4, 4.2, 4.5, 4.8, 5, 5.5, 6.2, 7.52]
time_taken_with_smart_contract = [4.96836256980896, 5, 5, 4.98, 5.1, 4.99, 5.01, 5, 5.012, 5.12]

# Plotting
plt.figure(figsize=(8, 5))
plt.plot(nodes, time_taken_without_smart_contract, marker='o', linestyle='-', color='b', label='Without Smart Contract')
plt.plot(nodes, time_taken_with_smart_contract, marker='o', linestyle='-', color='r', label='With Smart Contract')

# Adding labels and title
plt.xlabel('Number of Nodes')
plt.ylabel('Time Taken (seconds)')
plt.title('Impact of Network Size on Checking Node Status')
plt.legend()
plt.grid(True)

# Save the figure
plt.savefig('node_status_security.png')

# Set integer values on x-axis
plt.xticks(nodes)

# Show the plot
plt.show()
