import numpy as np
import random


class SegTree(object):
    """Use python list to build the segmented tree structure.
       Basic idea is to separate priority data and the tree in two lists."""
    def __init__(self, capacity):
        self.tree = np.zeros(2*capacity-1)  # tree structure
        self.data = np.zeros(capacity, dtype=object)  # record all transitions
        self.data_point = 0
        self.capacity = capacity

    def add(self, data, new_priority):
        self.data[self.data_point] = data
        tree_index = self.data_point + self.capacity - 1
        self.update(new_priority=new_priority, tree_index=tree_index)
        self.data_point += 1
        if self.data_point > self.capacity:
            self.data_point = 0

    def update(self, new_priority, tree_index):
        change = new_priority - self.tree[tree_index]
        self.tree[tree_index] = new_priority
        while tree_index != 0:
            tree_index = (tree_index - 1) // 2
            self.tree[tree_index] += change

    def get_capacity(self, leaf_index):
        return self.tree[leaf_index + self.capacity - 1]

    def get_sum(self):
        return self.tree[0]


class PrioritizedReplayBuff(object):
    def __init__(self, capacity):
        self.capacity = capacity
        self.segtree = SegTree(capacity=capacity)

    def add(self, data, new_capacity):
        self.segtree.add(data, new_capacity)

    def choose(self, batch_size):
        num_batch = self.capacity // batch_size
        res_collection = []
        print("tree sum: ", self.segtree.get_sum())
        for i in range(num_batch):
            search_index = 0  # search downward in the segment tree
            rand = random.uniform(0, self.segtree.get_sum())
            print("target to find position: ", rand)
            while True:
                if search_index > self.capacity - 1:  # reach the leafs
                    res_collection.append(self.segtree.tree[search_index])
                    break
                else:
                    l_son = 2 * search_index + 1
                    r_son = l_son + 1
                if self.segtree.tree[l_son] > rand:
                    search_index = l_son
                else:
                    search_index = r_son
                    rand = rand - self.segtree.tree[l_son]
        print("final search results: ", res_collection)


if __name__ == '__main__':
    buff = PrioritizedReplayBuff(capacity=10)
    for i in range(1, 11):
        data = 0.1
        buff.add(data, float(i)/10)
    buff.choose(batch_size=5)




    # test_sum_tree = SegTree(capacity=10)
    # for i in range(1, 11):
    #     # data = test_data([0, 0, 0, 0])
    #     data = 0.1
    #     test_sum_tree.add(data, float(i)/10)
    #
    # print "tree: ", test_sum_tree.tree
    # for j in range(test_sum_tree.capacity-1):
    #     print "parent: ", test_sum_tree.tree[j]
    #     print("left son: ", test_sum_tree.tree[2*j+1], " ; right son: ", test_sum_tree.tree[2*j+2])
    # print "sum: ", test_sum_tree.get_sum()




