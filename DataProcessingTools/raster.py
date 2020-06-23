from matplotlib.pyplot import gca
import numpy as np
from .objects import DPObject
from .spiketrain import Spiketrain
from .trialstructures import *
import os


class Raster(DPObject):
    def __init__(self, tmin, tmax, alignto=None, trial_event=None,
                 spiketimes=None,
                 trial_labels=None, dirs=None):
        if spiketimes is None:
            spiketrain = Spiketrain()
            spiketimes = spiketrain.timestamps.flatten()
        if alignto is None:
            trials = get_trials()
            # convert from seconds to ms
            alignto = 1000*trials.get_timestamps(trial_event)
        if trial_labels is None:
            trial_labels = np.arange(len(alignto))

        bidx = np.digitize(spiketimes, alignto+tmin)
        idx = (bidx > 0) & (bidx <= np.size(alignto))
        raster = spiketimes[idx] - alignto[bidx[idx]-1]
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
