import numpy as np
from matplotlib.pyplot import gcf, gca
from .objects import DPObject
from . import levels
from .raster import Raster
import os
import glob
import h5py
import hashlib


class PSTH(DPObject):
    """
    PSTH(bins,windowSize=1, dirs=None, redoLevel=0, saveLevel=1)
    """
    filename = "psth.hkl"
    argsList = ["bins", ("windowSize", 1)]
    level = "cell"

    def __init__(self, *args, **kwargs):
        """
        Return a PSTH object using the specified bins
        """
        DPObject.__init__(self, *args, **kwargs)
        self.indexer = self.getindex(self.level)

    def create(self, *args, **kwargs):
        saveLevel = kwargs.get("saveLevel", 1)
        bins = self.args["bins"]

        # attempt to load from the current directory
        kwargs["saveLevel"] = kwargs.get("saveLevel", 1) - 1
        kwargs["redoLevel"] = kwargs.get("redoLevel", 1) - 1
        raster = Raster(bins[0], bins[-1], **kwargs)
        spiketimes = raster.spiketimes
        trialidx = raster.trialidx
        self.trialLabels = raster.trialLabels

        ntrials = trialidx.max()+1
        counts = np.zeros((ntrials, np.size(bins)), dtype=np.int)
        for i in range(np.size(spiketimes)):
            jj = np.searchsorted(bins, spiketimes[i])
            if 0 <= jj < np.size(bins):
                counts[trialidx[i], jj] += 1

        windowSize = self.args["windowSize"]
        if windowSize > 1:
            scounts = np.zeros((ntrials, len(bins)-windowSize+1))
            for i in range(ntrials):
                for j in range(len(bins)-windowSize+1):
                    scounts[i, j] = counts[i, j:j+windowSize].sum()

            self.data = scounts
            self.bins = np.array(bins[:-windowSize])
        else:
            self.data = counts
            self.bins = np.array(bins)

        self.ntrials = ntrials

        # index to keep track of sets, e.g. trials
        self.setidx = [0 for i in range(self.ntrials)]

        self.plotopts = {"group_by_label": True}

    def append(self, psth):
        if not (self.bins == psth.bins).all():
            ValueError("Incompatible bins")

        DPObject.append(self, psth)
        self.data = np.concatenate((self.data, psth.data), axis=0)
        self.trialLabels = np.concatenate((self.trialLabels, psth.trialLabels),
                                           axis=0)
        self.ntrials = self.ntrials + psth.ntrials

    def plot(self, i=None, ax=None, overlay=False):
        self.current_idx = i
        if i is None:
            pidx = range(len(self.trialLabels))
        else:
            pidx = self.indexer(i)
        if ax is None:
            ax = gca()
        if not overlay:
            ax.clear()
        trialLabels = self.trialLabels[pidx]
        data = self.data[pidx, :]
        labels = np.unique(trialLabels)
        if self.plotopts["group_by_label"]:
            for li in range(len(labels)):
                label = labels[li]
                idx = trialLabels == label
                mu = data[idx, :].mean(0)
                sigma = data[idx, :].std(0)
                ax.plot(self.bins, mu)
                ax.fill_between(self.bins, mu-sigma, mu+sigma)
        else:
            # collapse across labels
            mu = data.mean(0)
            sigma = data.std(0)
            ax.plot(self.bins, mu)
            ax.fill_between(self.bins, mu-sigma, mu+sigma)

