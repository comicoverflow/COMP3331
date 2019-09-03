# COMP3331 Assignment 1 - Priority Queue
# Priority queue heap structure
# Code referenced from COMP2521 assignment 2 in semester 2, 2017
# https://github.com/anthonyaxu/COMP2521/blob/master/assignment%202/PQ.c
# Translated from C to Python and modifed to work with the link state routing nodes
# Minimum priority queue meaning the smallest value is always at the beginning of
# the list (index 1 in this case)
# z5165674

import sys

# Pre-defined value in array that references the distance
VALUE = 1

class PQ():
    def __init__(self):
        self._queue = []
        # First index must not be used to store any real values
        self._queue.append(None)

    def get_queue(self):
        return self._queue

    def get_right_child(self, index):
        return int(2*index + 1)

    def get_left_child(self, index):
        return int(2*index)

    def get_parent(self, index):
        return int(index/2)

    # Check if the node is in the queue
    def check_node(self, node):
        for i in range(1, len(self._queue)):
            if self._queue[i][0] == node:
                return True
        return False

    # Swaps two nodes
    def swap_nodes(self, index1, index2):
        self._queue[index1], self._queue[index2] = self._queue[index2], self._queue[index1]

    # If node exists in the queue, return the array/list index
    def get_index(self, node):
        for i in range(1, len(self._queue)):
            if self._queue[i][0] == node:
                return i
        return -1

    # Move an element up the queue
    def shift_up(self, index):
        while index != 1:
            parent = self.get_parent(index)
            # If child is greater than the parent, do nothing
            if self._queue[index][VALUE] > self._queue[parent][VALUE]:
                break
            else:
                self.swap_nodes(index, parent)
            index = parent

    # Move an element down the queue
    def shift_down(self, index):
        loop_break = 0
        while True:
            left_child = self.get_left_child(index)
            right_child = self.get_right_child(index)
            parent = index

            # If the right child is out of bounds
            if right_child >= len(self._queue):
                # If the left child is out of bounds
                if left_child >= len(self._queue):
                    break
                swap_child = left_child
                loop_break = 1
            elif self._queue[left_child][VALUE] < self._queue[right_child][VALUE]:
                swap_child = left_child
            else:
                swap_child = right_child
            # If child is smaller than the parent
            if self._queue[parent][VALUE] > self._queue[swap_child][VALUE]:
                self.swap_nodes(parent, swap_child)
                index = swap_child
            else:
                break
            if loop_break == 1:
                break
    
    # Check if the priority queue needs to be updated
    def update(self, node, dist):
        index = self.get_index(node)
        if index == -1:
            sys.exit(1)
        else:
            self._queue[index][VALUE] = dist
            parent = self.get_parent(index)
            left_child = self.get_left_child(index)
            right_child = self.get_right_child(index)

            # If node is at the bottom/end
            if left_child > len(self._queue) and right_child > len(self._queue):
                # Check if index value is less than the parent's value
                if self._queue[index][VALUE] < self._queue[parent][VALUE]:
                    self.shift_up(index)
            elif index == 1:
                self.shift_down(index)
            elif self._queue[index][VALUE] > self._queue[index][VALUE]:
                self.shift_down(index)
            else:
                self.shift_up(index)

    # Insert an node to the list, then reshuffle it
    def insert(self, node, dist):
        if self.check_node(node):
            # If the node is already in the queue
            self.update(node, dist)
        else:
            item = [node, dist]
            self._queue.append(item)
            index = len(self._queue) - 1
            if index > 1:
                self.shift_up(index)
    
    # Remove the first node of the list, then reshuffle it
    def pop(self):
        head = self._queue.pop(1)
        if not self.is_empty():
            self.shift_down(1)
        return head

    def is_empty(self):
        if self._queue[0] == None and len(self._queue) == 1:
            return True
        else:
            return False