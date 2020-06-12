import numpy as np


class DPObject():
    def __init__(self, *args, **kwargs):
        self.data = np.ndarray((0, 0))

    def plot(self, i, fig):
        pass

    def __add__(self, obj):
        pass

    def level(self):
        pass

    def update_idx(self, index):
        """
        Return `index` if it is valid for the current object
        """
        return max(0, min(index, self.data.shape[0]-1))
