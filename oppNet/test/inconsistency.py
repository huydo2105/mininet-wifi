import matplotlib.pyplot as plt

# Original data
# Dummy data
nodes = [9, 12, 15, 18, 21, 24, 27, 30, 33, 36]
time_taken_without_smart_contract = [6, 11.51, 18.12, 29.1432, 42.251, 48.229, 62, 68, 73, 78]
time_taken_with_smart_contract = [5.274924278259277, 6.2259712, 8.65452, 9.872, 12.1233, 15.124, 17.675, 20, 22.54, 28.12]       
offline_hosts = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # Example data for number of offline hosts


# Plotting
plt.figure(figsize=(8, 5))
plt.plot(nodes, time_taken_without_smart_contract, marker='o', linestyle='-', color='b', label='Without Smart Contract')
plt.plot(nodes, time_taken_with_smart_contract, marker='o', linestyle='-', color='r', label='With Smart Contract')

# Plotting number of offline hosts
plt.plot(nodes, offline_hosts, marker='x', linestyle='--', color='g', label='Inconsistent Nodes')

# Adding labels and title
plt.xlabel('Number of Nodes')
plt.ylabel('Time Taken (seconds)')
plt.title('Impact of Network Size on Route Finding with Inconsistent Nodes')
plt.legend()
plt.grid(True)

# Set x-axis ticks to integer values
plt.xticks(nodes)

# Save the figure
plt.savefig('route_finding_performance_with_offline_hosts.png')

# Show the plot
plt.show()
