import numpy as np


class OU(object):
    """
    Ornstein-Uhlenbeck process
    """
    def function(self, x, mu, theta, sigma):
        return theta * (mu - x) + sigma * np.random.randn(1)

