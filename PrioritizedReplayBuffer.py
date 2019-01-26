import numpy as np
import random


class SegTree(object):
    """Use python list to build the segmented tree structure.
       Basic idea is to separate priority and the tree in two lists."""
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
        if self.data_point >= self.capacity:
            self.data_point = 0

    def update(self, new_priority, tree_index):
        change = new_priority - self.tree[tree_index]
        self.tree[tree_index] = new_priority
        while tree_index != 0:
            tree_index = (tree_index - 1) // 2
            self.tree[tree_index] += change

    def get_leaf(self, v):
        """
        :param v: priority value to search in the segment tree
        :return:  [leaf_index: result leaf index in the tree;
                  leaf: result priority value;
                  data: corresponding transitions in the data collection]
        """
        parent_index = 0  # search downward in the segment tree
        while True:
            l_son = 2 * parent_index + 1
            r_son = l_son + 1
            if l_son > self.capacity - 1:  # reach the leafs
                leaf_index = l_son
                break
            else:
                if self.tree[l_son] >= v:
                    parent_index = l_son
                else:
                    parent_index = r_son
                    v -= self.tree[l_son]
        data_index = leaf_index - (self.capacity - 1)
        return leaf_index, self.tree[leaf_index], self.data[data_index]

    def get_capacity(self, leaf_index):
        return self.tree[leaf_index + self.capacity - 1]

    def get_sum(self):
        return self.tree[0]


class PrioritizedReplayBuff(object):
    def __init__(self, capacity):
        self.capacity = capacity
        self.segtree = SegTree(capacity=capacity)
        self.alpha = 0.1
        self.beta = 0.1
        self.max_beta = 1.
        self.delta_beta = 0.001
        self.epsilon = 0.001

    def store(self, data):
        max_p = max(self.segtree[-self.capacity:])
        if max_p == 0.:  # initial state
            max_p = 1.
        self.segtree.add(data, max_p)

    def sample(self, batch_size):
        """sample a batch in the buffer according to the priorities"""
        step_rand = self.capacity // batch_size
        p_collection = []
        index_collection = []
        data_collection = []
        rands = []
        for i_rand in range(batch_size):
            a, b = i_rand*step_rand, (i_rand + 1)*step_rand
            rand = random.uniform(a, b)
            rands.append(rand)
            i_index, i_p, i_data = self.segtree.get_leaf(rand)
            index_collection.append(i_index)
            p_collection.append(i_p)
            data_collection.append(i_data)
        print("randoms are: ", rands)
        print("final priority results: ", p_collection)
        print("final index results: ", index_collection)
        return index_collection, p_collection, data_collection

    def choose_and_update(self, batch_size, TD_err):
        """choose the priorities in the buffer and renew the parameters"""
        # sample a batch of priorities
        index_collection, p_collection, data_collection = self.sample(batch_size)
        P_s = pow(p_collection, self.alpha) / sum(pow(p_collection, self.alpha))
        w_s = pow(1/batch_size/P_s, self.beta)

        self.beta += self.delta_beta
        self.beta = min(self.beta, 1.)


if __name__ == '__main__':
    buff = PrioritizedReplayBuff(capacity=8)
    for i in range(1, 9):
        data = 0.1
        buff.add(data, float(i))
    buff.choose(batch_size=2)




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




