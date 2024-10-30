import socket
import argparse
import os

# Setup argument parser to receive station name and IP address
parser = argparse.ArgumentParser(description='Station Beacon Listener')
parser.add_argument('--name', type=str, required=True, help='Name of the station')
parser.add_argument('--ip', type=str, required=False, default="0.0.0.0", help='IP address of the station')

# Parse arguments
args = parser.parse_args()

station_name = args.name
UDP_IP = args.ip
UDP_PORT = 5005  

print("Station {} starting to listen on {}:{}".format(station_name, UDP_IP, UDP_PORT))

# Create socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP

try:
    sock.bind((UDP_IP, UDP_PORT))
    print("Socket successfully bound to {}:{}".format(UDP_IP, UDP_PORT))
except OSError as e:
    print("Failed to bind socket: {}".format(e))
    exit(1)

# Define file paths
data_file_path = "{}.txt".format(station_name)
signal_file_path = "{}.signal".format(station_name)

# Empty both files at the start
open(data_file_path, 'w').close()  # Create or clear the data file
open(signal_file_path, 'w').close()  # Create or clear the signal file

# Listen for incoming messages
while True:
    data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
    message = data.decode('utf-8')

    print("Station {} received message from {}: {}".format(station_name, addr, message))

    # Append the latest message to the data file
    with open(data_file_path, 'a') as data_file:  # Use 'a' for append mode
        data_file.write(message)  # Add a newline for readability

    # Update the signal file to indicate new data
    with open(signal_file_path, "w"):
        pass
