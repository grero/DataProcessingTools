from matplotlib.pyplot import gca
import numpy as np
from .objects import DPObject
from .spiketrain import Spiketrain
from .trialstructures import *
import os


class Raster(DPObject):
    """
    Raster(tmin, tmax, TrialEvent,trialType, sortBy)
    """
    filename = "raster.hkl"
    argsList = ["tmin", "tmax", "trialEvent", "trialType", "sortBy"]
    level = "cell"

    def __init__(self, *args, **kwargs):
        DPObject.__init__(self, *args, **kwargs)

    def create(self, *args, **kwargs):
        trials = get_trials()
        #TODO: This only works with correct trials for now
        rewardOnset, cidx, stimIdx = trials.get_timestamps("reward_on")
        trialEvent = self.args["trialEvent"]
        if "stimulus" in trialEvent:
            if trialEvent == "stimulus1":
                stimnr = 0
            elif trialEvent == "stimulus2":
                stimnr = 1
            else:
                stimnr = -1
                ValueError("Unkonwn trial sorting {0}".format(trialEvent))

            alignto, stimidx, trialLabel = trials.get_stim(stimnr, cidx)
            alignto = 1000*np.array(alignto)
        else:
            alignto, sidx, stimIdx = trials.get_timestamps(trialEvent)
            qidx = np.isin(sidx, cidx)
            trialIdx = sidx[qidx]
            alignto = 1000*alignto[qidx]
            sortBy = self.args["sortBy"]
            if sortBy == "stimulus1":
                stimnr = 0
            elif sortBy == "stimulus2":
                stimnr = 1
            else:
                ValueError("Unkonwn trial sorting {0}".format(sortBy))

            ts, identity, trialLabel = trials.get_stim(stimnr, trialIdx)
        #TODO: Never reload spike trains
        spiketrain = Spiketrain(*args, **kwargs)
        spiketimes = spiketrain.timestamps.flatten()
        tmin = self.args["tmin"]
        tmax = self.args["tmax"]
        bidx = np.digitize(spiketimes, alignto+tmin)
        idx = (bidx > 0) & (bidx <= np.size(alignto))
        raster = spiketimes[idx] - alignto[bidx[idx]-1]
        ridx = (raster > tmin) & (raster < tmax)
        self.spiketimes = raster[ridx]
        self.trialidx = bidx[idx][ridx]-1
        self.trialLabels = trialLabel
        self.setidx = [0 for i in range(len(self.trialidx))]
        self.plotopts = {}

    def append(self, raster):
        DPObject.append(self, raster)
        n_old = len(self.spiketimes)
        n_new = n_old + len(raster.spiketimes)
        self.spiketimes = np.resize(self.spiketimes, n_new)
        self.spiketimes[n_old:n_new] = raster.spiketimes
        self.trialidx = np.resize(self.trialidx, n_new)
        self.trialidx[n_old:n_new] = raster.trialidx

        self.trialLabels = np.concatenate((self.trialLabels, raster.trialLabels))

    def plot(self, i=None, ax=None, overlay=False):
        if ax is None:
            ax = gca()
        if not overlay:
            ax.clear()
        if i is None:
            # plot everything
            pidx = range(len(self.spiketimes))
        else:
            pidx = self.indexer(i)
        ax.plot(self.spiketimes[pidx], self.trialidx[pidx], '.')
