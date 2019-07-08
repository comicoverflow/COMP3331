#!/usr/bin/python3
# COMP3331 Lab 2 Question 5
# Anthony Xu - z5165674

import time
import socket
import sys

# Calculate the averge for the values in the times list
def calculate_average(times):
    length = len(times)
    total = 0
    for rtt in times:
        total += rtt

    average = total / length

    return round(average, 1)


# Assuming that input is always valid
host = sys.argv[1]
port = int(sys.argv[2])

address = (host, port)

# Creating the socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Set the timeout of the request to be 1 second, socket is non-blocking
client_socket.settimeout(1)

# List/Array to store RTT to calculate min, max and average
rtt_times = []

for ping in range(0, 10):

    # Grab the time the message is sent to the socket
    start_time = time.time()

    # Creating the message
    message = "PING " + str(ping) + " " + str(start_time) + " \r\n"
    # Convert the string to bytes (so that the socket can read it)
    msg = bytes(message, "utf-8")
    # Send the message to the socket
    client_socket.sendto(msg, address)

    try:
        # Collecting data from the socket
        data, socket_address = client_socket.recvfrom(1024)
        # Getting the time the ddata was received
        end_time = time.time()

        # Calculating the round trip time for the packets
        rtt_seconds = end_time - start_time
        # Converting into milliseconds and round off to one decimal place
        rtt_milliseconds = round(rtt_seconds * 1000, 1)

        # Store the RTT
        rtt_times.append(rtt_milliseconds)

        print("ping to " + str(host) + ", seq = " + str(ping) + ", rtt = " + str(rtt_milliseconds) + " ms")

    # Timeout when the server takes longer than 1 second to reply
    except socket.timeout:
        print("ping to " + str(host) + ", seq = " + str(ping) + ", time out")

# Sort the list in ascending order
rtt_times.sort()
# Assign the first element in the list to min (the smallest value)
min = rtt_times[0]
# Assign the last element in the list to max (the largest value)
max = rtt_times[len(rtt_times) - 1]
# Calculate the average of the elements in rtt_times
mean = calculate_average(rtt_times)

# Print out numbers
print()
print("Minimum RTT: " + str(min) + " ms")
print("Maximum RTT: " + str(max) + " ms")
print("Mean RTT: " + str(mean) + " ms")