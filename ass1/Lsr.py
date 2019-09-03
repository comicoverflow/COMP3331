#!/bin/usr/python3
# COMP3331 Assignment 1 - Link State Routing
# Anthony Xu - z5165674

import sys
import time
import pickle
import threading
from socket import *

from Graph import Graph
from dijkstra import *

# Pre-defined variables
# Time between routers sending out packets
UPDATE_INTERVAL = 1
# Time between the dijkstra algorithm is called
ROUTE_UPDATE_INTERVAL = 30
# Time before function begins checking router states
ROUTER_STATE_STARTUP = 18
# Time between routers sending keep alive messages
HEARTBEAT_INTERVAL = 0.3
# IP address for sockets to send to
SOCKET_IP = "localhost"

# Global variables
# Number identifying packets sent out by router
sequence_number = 0
# Number of neighbours a router has
no_of_neighbours = 0
# Name of the router running the program
current_router = ""
# List of the router's neighbours
neighbours = []
# Contains the sequence nnumber of packets sent from each router
packet_dictionary = {}
# Contains the time the last keep alive message was went
last_alive_message = {}
# Graph variable for storing the routers and links between them
graph = {}


# Socket for receiving packets
server_socket = socket(AF_INET, SOCK_DGRAM)
# Socket for sending packets
client_socket = socket(AF_INET, SOCK_DGRAM)
# Lock for threads
lock = threading.Lock()


# Function to return the contents of a given file
def read_file(file_name):
    f = open(file_name, "r")
    if f.mode == "r":
        # Read each line of the line
        contents = f.readlines()
    f.close()
    return contents


# Append the neighbours of the current node/router to a list
def create_neighbours(data):
    global no_of_neighbours, neighbours

    for i in range(2, 2 + no_of_neighbours):
        temp_ = data[i].split()
        # Each neighbour is contained in a dictionary with all the information
        node = {"id": temp_[0], "cost": float(temp_[1]), "port": int(temp_[2]), "status": "alive"}
        neighbours.append(node)


# Function to create a packet based on the current node/router's information
def create_packet(message):
    global current_router, no_of_neighbours, neighbours

    # Time when packet was created and sent
    send_time = time.time()

    # Add rest of the router's information to packet
    message.append(current_router)
    message.append(no_of_neighbours)
    message.append(neighbours)
    message.append(send_time)

    return message


# Current router will send packets to its neighbours every one second
def send():
    global neighbours, no_of_neighbours, client_socket, SOCKET_IP, sequence_number, UPDATE_INTERVAL

    while True:
        # Initiate the packet, the sequence number is the same for every round of packet sends
        packet = []
        packet.append(sequence_number)
        sequence_number += 1
        # Add other information to the packet
        packet = create_packet(packet)
        # For each of the router's neighbours, send the packet only if they are alive
        for i in range(0, no_of_neighbours):
            if neighbours[i]["status"] == "alive":
                neighbour_port = neighbours[i]["port"]
                address = (SOCKET_IP, neighbour_port)
                client_socket.sendto(pickle.dumps(packet), address)

        # Wait 1 second before creating and sending another packet to neighbours
        time.sleep(UPDATE_INTERVAL)


# Current router will receive packets and create new nodes for any packet it receives from new routers
# Re-transmits the incoming packet to its own neighbours
def receive():
    global packet_dictionary, server_socket, client_socket, graph, neighbours, last_alive_message, lock, SOCKET_IP

    while True:
        # Receive packet from a neighbour and then decode and covert it into a list for reading
        received_packet, receiver_address = server_socket.recvfrom(4096)
        message = pickle.loads(received_packet)

        # If the message is a keep alive/heartbeat message
        if message[0] == "alive":
            alive_node = message[1]
            received_time = time.time()
            lock.acquire()
            # Update the most recent time the socket received a keep alive message
            last_alive_message[alive_node] = received_time
            lock.release()
        else:
            # Split the information received from the packet
            seq_number = message[0]
            sender_id = message[1]
            sender_no_of_neighbours = message[2]
            sender_neighbours = message[3]
            receive_time = message[4]

            # If this is the first time receiving the packet from a router, add the router to the packet dictionary
            if sender_id not in packet_dictionary:
                # Add router id to dictionary and the packet's sequence number
                packet_dictionary.update({sender_id: []})

            # If the router hasn't received this sequence number before, add router to graph and add edges
            # Makes sure that the router does not send a packet that is has already sent
            if seq_number not in packet_dictionary[sender_id]:
                packet_dictionary[sender_id].append(seq_number)
                lock.acquire()
                # Add the router to graph, graph will handle if the router already exists
                graph.add_vertex(sender_id)
                for n in sender_neighbours:
                    # If the neighbour is alive, add the edge to the graph
                    if n["status"] == "alive":
                        graph.add_edge(sender_id, n["id"], n["cost"])
                    else:
                        # Remove the edge (if it exists) from the graph, the graph class will handle duplicates
                        graph.remove_vertex(n["id"])
                lock.release()

                # Send the received packet to its own neighbours
                for n in neighbours:
                    # Don't send the packet back to the node it received it from and only send to neighbours that are alive
                    if n["id"] != sender_id and n["status"] == "alive":
                        neighbour_port = n["port"]
                        address = (SOCKET_IP, neighbour_port)
                        client_socket.sendto(received_packet, address)


# Call the dijsktra algorithm to calculate shortest path then print them out with their cost
def print_path():
    global graph, current_router, ROUTE_UPDATE_INTERVAL

    while True:
        # Wait 30 seconds between each dijkstra call
        time.sleep(ROUTE_UPDATE_INTERVAL)
        print("I am router " + current_router)
        for node in graph.get_vertices():
            if node != current_router:
                # Calculate the shortest path between two nodes
                path = shortest_path(graph, current_router, node)
                print("Least cost path to router " + node + ": ", end="")

                # Print out the path from src to dest and calculate the cost
                cost = 0
                for i in range(0, len(path) - 1):
                    cost += graph.find_edge(path[i], path[i + 1])
                    print(path[i], end="")
                print(path[len(path) - 1], end="")

                print(" and the cost: ", end="")
                print("{0:0.1f}".format(cost))


# Checks the state of the neighbouring routers
# Classed as dead if is hasn't sent a keep alive message within a certain time period
# else, classed as alive
def check_router_state():
    global neighbours, no_of_neighbours, last_alive_message, graph, lock, HEARTBEAT_INTERVAL, ROUTER_STATE_STARTUP

    # Wait until all heartbeat messages have been sent
    time.sleep(ROUTER_STATE_STARTUP)
    while True:
        for i in range(0, no_of_neighbours):
            router_name = neighbours[i]["id"]
            time_check = time.time()
            lock.acquire()
            
            try:
                # Check if the last sent heartbeat message was sent within three HEARTBEAT_INTERVAL's
                if time_check > (last_alive_message[router_name] + 3*HEARTBEAT_INTERVAL):
                    # Remove the router from the graph, and all its links
                    graph.remove_vertex(router_name)
                    # Change the status of the neighbour to dead
                    neighbours[i]["status"] = "dead"

                # If the neighbour is alive, add it back to the graph (if not already in)
                else:
                    # The edges will be added to the graph the next time the router receives a packet from the neighbour
                    graph.add_vertex(router_name)
                    # Change the status of the neighbour back to alive
                    neighbours[i]["status"] = "alive"

                lock.release()
            # If router is not yet initialised in dictionary, continue and try again
            except KeyError:
                pass


# Sends a message every HEARTBEAT_INTERVAL seconds to its neighbours telling them they are alive
def heartbeat():
    global client_socket, neighbours, no_of_neighbours, current_router, SOCKET_IP, HEARTBEAT_INTERVAL

    while True:
        for i in range(0, no_of_neighbours):
            # Send the message to every neighbour that is alive
            if neighbours[i]["status"] == "alive":
                neighbour_port = neighbours[i]["port"]
                address = (SOCKET_IP, neighbour_port)
                # Message only contains the alive string and which router sent it
                heartbeat_message = ["alive", current_router]
                client_socket.sendto(pickle.dumps(heartbeat_message), address)
        
        # Wait HEARTBEAT_INTERVAL seconds before sending another heartbeat message
        time.sleep(HEARTBEAT_INTERVAL)


def main():
    global current_router, no_of_neighbours, graph, server_socket, SOCKET_IP

    # Checking for only one input file
    if len(sys.argv) != 2:
        print("Usage: python3 Lsr.py <input file>")
        sys.exit(1)

    # Read input file and copy to 'data' variable
    file_name = sys.argv[1]
    data = read_file(file_name)
    # Grab id and port number for current node/router
    temp_ = data[0].split()
    current_router = temp_[0]
    socket_port = int(temp_[1])

    no_of_neighbours = int(data[1])
    # Create list of the router's neighbours
    create_neighbours(data)

    # Initialise graph
    graph = Graph(graph)

    # Bind the receiving socket to the correct IP
    address = (SOCKET_IP, socket_port)
    server_socket.bind(address)

    # Initiate and start each thread
    sender = threading.Thread(target=send)
    sender.daemon = True
    sender.start()
    
    receiver = threading.Thread(target=receive)
    receiver.daemon = True
    receiver.start()
    
    dijsktra_thread = threading.Thread(target=print_path)
    dijsktra_thread.daemon = True
    dijsktra_thread.start()

    heartbeat_thread = threading.Thread(target=heartbeat)
    heartbeat_thread.daemon = True
    heartbeat_thread.start()

    check_router_thread = threading.Thread(target=check_router_state)
    check_router_thread.daemon = True
    check_router_thread.start()

    sender.join()
    receiver.join()
    dijsktra_thread.join()
    heartbeat_thread.join()
    check_router_thread.join()


if __name__ == "__main__":
    main()