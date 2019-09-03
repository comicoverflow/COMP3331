# COMP3331 Assignment 1 - Dijsktra's Algorithm
# Created following pseudocode on the Dijsktra Wikipedia page
# and modifed to work alongside Lsr.py
# https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
# z5165674

from Graph import Graph
from PQ import PQ

INFINITY = float('inf')

# Dijkstra's Algorithm modified from pseudocode from Wikipedia
def dijkstra(graph, src, dest = None):
    distance = {}
    previous = {}

    p = PQ()
    distance[src] = 0

    # Set the distance from src to every other node to infinity
    for v in graph.get_vertices():
        if v != src:
            distance[v] = INFINITY
        previous[v] = None
        # Add each node to the priority queue
        p.insert(v, distance[v])

    while not p.is_empty():
        # Return the node with the smallest distance value
        u = p.pop()
        node = u[0]
        for n in graph.get_graph()[node]:
            # Calculate a new distance between the nodes
            value = distance[node] + graph.find_edge(n[0], node)
            if value < distance[n[0]]:
                # Update priority queue and dictionaries
                distance[n[0]] = value
                previous[n[0]] = node
                p.update(n[0], value)
    
    return distance, previous


# Calculate the shortest path between the source and destination node
def shortest_path(graph, src, dest):
    dist, prev = dijkstra(graph, src, dest)
    path = []
    while True:
        path.append(dest)
        if dest == src:
            break
        dest = prev[dest]
    path.reverse()

    return path