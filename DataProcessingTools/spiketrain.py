from .objects import DPObject
import numpy as np
import scipy.io as sio
import os


class Spiketrain(DPObject):
    def __init__(self):
        DPObject.__init__(self)
        self.level = "cell"
        self.filename = "unit.mat"
        if os.path.isfile(self.filename):
            self.load()

    def load(self):
        q = sio.loadmat(self.filename)
        self.timestamps = q["timestamps"]
        self.spikeshape = q["spikeForm"]
