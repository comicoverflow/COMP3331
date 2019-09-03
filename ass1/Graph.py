# COMP3331 Assignment 1 - Graph
# Dictionary with each key being the vertex of a node
# Linking node and cost contained inside a list
# eg. {"A": [["B", 10], ["E", 2.7]], "B": [["A", 10]], "E": [["A", 2.7]]}
# z5165674

class Graph():
    def __init__(self, graph):
        self._graph = graph

    def get_graph(self):
        return self._graph

    def get_vertices(self):
        return self._graph.keys()

    # If the vertex is not already in the graph, add the vertex
    def add_vertex(self, v):
        if v not in self._graph:
            self._graph[v] = []

    # Removes the vertex from the graph and any corresponding edges
    def remove_vertex(self, v):
        if v in self._graph:
            self._graph.pop(v)
            # Check for the edge in each vertex
            for i in self.get_vertices():
                temp_ = []
                for j in range(0, len(self._graph[i])):
                    # If only one edge, remove it
                    if len(self._graph[i]) == 1:
                        if self._graph[i][j][0] == v:
                            self._graph[i].remove(self._graph[i][j])

                    # else, create a new list containing everything but the deleted vertex
                    else:
                        if self._graph[i][j][0] != v:
                            temp_.append(self._graph[i][j])
                # Update the vertex with the new edges
                if len(temp_) > 0:
                    self._graph[i] = temp_

    # Finds the edge between two nodes and returns the cost/value
    def find_edge(self, n1, n2):
        for i in range(0, len(self._graph[n1])):
            if self._graph[n1][i][0] == n2:
                return self._graph[n1][i][1]
        return None

    def add_edge(self, n1, n2, value):
        # Adds vertices to graph in case they are not present. Won't affect anything if they are already in the graph
        self.add_vertex(n1)
        self.add_vertex(n2)
        # Check if the edge already exists in graph, if not, add edges
        if self.find_edge(n1, n2) == None:
            edge1 = [n2, value]
            self._graph[n1].append(edge1)
            edge2 = [n1, value]
            self._graph[n2].append(edge2)