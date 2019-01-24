import numpy as np
import random


class SegTree(object):
    """Use python list to build the segmented tree structure.
       Basic idea is to separate priority data and the tree in two lists."""
    def __init__(self, capacity):
        self.tree = np.zeros(shape=[2*capacity+1, 1])  # tree structure
        self.data = np.zeros(shape=[capacity, 1], dtype=object)  # record all transitions
        self.data_point = 0
        self.capacity = capacity

    def add(self, data, new_priority):
        self.data[self.data_point] = data
        tree_index = self.data_point + self.capacity - 1
        self.data_point = self.data_point + 1
        if self.data_point > len(self.data):
            self.data_point = 0
        change = new_priority - self.tree[tree_index]
        self.update(change=change, tree_index=tree_index)

    def update(self, change, tree_index):
        while True:
            self.tree[tree_index] += change
            parent = (tree_index - 1) // 2
            if parent < 0:
                break
            else:
                self.tree[parent] += change

    def get_sum(self):
        return self.tree[0]


class test_data(object):
    def __init__(self, data):
        self.data = data


if __name__ == '__main__':
    test_sum_tree = SegTree(capacity=10)
    for i in range(9):
        # data = test_data([0, 0, 0, 0])
        data = 0
        test_sum_tree.add(data, i/9)

    print ("sum: ", test_sum_tree.get_sum())




