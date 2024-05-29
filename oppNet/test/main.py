import matplotlib.pyplot as plt

# Dummy data
nodes = [9, 12, 15, 18, 21, 24, 27, 30, 33, 36]
time_taken_without_smart_contract = [3.5, 8.531, 15.213, 24.123, 39.251, 45.912, 60, 65, 70, 75]
time_taken_with_smart_contract = [4.96836256980896, 5, 7, 8.815, 10, 12, 15, 18, 20, 25]

# Plotting
plt.figure(figsize=(8, 5))
plt.plot(nodes, time_taken_without_smart_contract, marker='o', linestyle='-', color='b', label='Without Smart Contract')
plt.plot(nodes, time_taken_with_smart_contract, marker='s', linestyle='-', color='r', label='With Smart Contract')

# Adding labels and title
plt.xlabel('Number of Nodes')
plt.ylabel('Time Taken (seconds)')
plt.title('Impact of Network Size on Route Finding')
plt.legend()
plt.grid(True)


# Set integer values on x-axis
plt.xticks(nodes)

# Save the figure
plt.savefig('route_finding_performance.png')



# Show the plot
plt.show()
