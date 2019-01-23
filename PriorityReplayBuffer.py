from collections import deque
import random
from ReplayBuffer import ReplayBuffer


class SegTreeNode(object):
    def __init__(self, value):
        self.value = value
        self.l_node = None
        self.r_node = None

    def set_value(self, value):
        self.value = value
        return

    def get_value(self):
        return self.value


class SegTree(object):
    def __init__(self, is_leaf=False, v_root=None, v_left_node=None, v_right_node=None):
        self.root_node = SegTreeNode(v_root)
        if not is_leaf:
            self.l_node = SegTreeNode(v_left_node)
            self.r_node = SegTreeNode(v_right_node)
        else:
            self.l_node, self.r_node = None, None

    def set_left_node(self, value):
        self.l_node = SegTreeNode(value)

    def set_right_node(self, value):
        self.r_node = SegTreeNode(value)

    def get_son_values(self):
        return self.l_node.get_value(), self.r_node.get_value()

    def get_son_nodes(self):
        return self.l_node, self.r_node

    def calculate_root_value(self):
        self.root_node.set_value(self.l_node.get_value() + self.r_node.get_value())

    def get_root_value(self):
        return self.root_node.get_value()


class PriorityReplayBuffer(ReplayBuffer):
    def __init__(self, buffer_size):
        ReplayBuffer.__init__(self, buffer_size)

    def build_seg_tree(self, batch_size):
        this_size = max(self.buffer_size, self.num_experiences)
        num_segs = this_size // batch_size
        
        for i in range(0,num_segs,2):







