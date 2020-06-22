from matplotlib.pyplot import gca
import numpy as np
from .objects import DPObject
from .spiketrain import Spiketrain
import os


class Raster(DPObject):
    def __init__(self, tmin, tmax, spiketimes=None, 
                 trial_event=None,  trial_labels=None,
                 dirs=None):
        bidx = np.digitize(spiketimes, trial_event+tmin)
        if spiketimes is None:
            spiketrain = Spiketrain()
            spiketimes = spiketrain.timestamps
        if trial_event is None:
            # TODO: Load trials here
            pass
        if trial_labels is None:
            trial_labels = np.arange(len(trial_event))

        idx = (bidx > 0) & (bidx <= np.size(trial_event))
        raster = spiketimes[idx] - trial_event[bidx[idx]-1]
        ridx = (raster > tmin) & (raster < tmax)
        self.spiketimes = raster[ridx]
        self.trialidx = bidx[idx][ridx]-1
        self.trial_labels = trial_labels
        self.setidx = [0 for i in range(len(trial_labels))]
        if dirs is None:
            self.dirs = [os.getcwd()]
        else:
            self.dirs = dirs

    def plot(self, idx=None, ax=None, overlay=False):
        if ax is None:
            ax = gca()
        if not overlay:
            ax.clear()
        if idx is None:
            # plot everything
            idx = range(len(self.spiketimes))
        ax.plot(self.spiketimes[idx], self.trialidx[idx], '.')
