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
    filename = "psth.mat"
    argsList = ["bins", ("windowSize", 1)]

    def __init__(self, *args, **kwargs):
        """
        Return a PSTH object using the specified bins
        """
        DPObject.__init__(self, *args, **kwargs)

    def create(self, *args, **kwargs):
        saveLevel = kwargs.get("saveLevel", 1)
        bins = self.args["bins"]

        # attempt to load from the current directory
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
            scounts = np.zeros((ntrials, len(bins)-windowSize))
            for i in range(ntrials):
                for j in range(len(bins)-windowSize):
                    scounts[i, j] = counts[i, j:j+windowSize].sum()

            self.data = scounts
            self.bins = np.array(bins[:-windowSize])
        else:
            self.data = counts
            self.bins = np.array(bins)

        self.ntrials = ntrials

        # index to keep track of sets, e.g. trials
        self.setidx = [0 for i in range(self.ntrials)]
        
        if saveLevel > 0:
            self.save()

    def load(self, fname=None):
        DPObject.load(self)
        if fname is None:
            fname = self.filename
        with h5py.File(fname) as ff:
            args = {}
            for (k,v) in ff["args"].items():
                self.args[k] = v
            self.data = ff["counts"][:]
            self.ntrials = self.data.shape[0]
            self.bins = self.args["bins"][:self.data.shape[-1]]
            self.trialLabels = ff["trialLabels"][:]

    def hash(self):
        """
        Returns a hash representation of this object's arguments.
        """
        #TODO: This is not replicable across sessions
        h = hashlib.sha1(b"psth")
        for (k, v) in self.args.items():
            x = np.atleast_1d(v)
            h.update(x.tobytes())
        return h.hexdigest()

    def save(self, fname=None):
        if fname is None:
            fname = self.get_filename()

        with h5py.File(fname, "w") as ff:
            args = ff.create_group("args")
            args["bins"] = self.args["bins"]
            args["windowSize"] = self.args["windowSize"]
            ff["counts"] = self.data
            ff["trialLabels"] = self.trialLabels
            ff["dirs"] = np.array(self.dirs, dtype='S256')
            ff["setidx"] = self.setidx

    def append(self, psth):
        if not (self.bins == psth.bins).all():
            ValueError("Incompatible bins")

        DPObject.append(self, psth)
        self.data = np.concatenate((self.data, psth.data), axis=0)
        self.trialLabels = np.concatenate((self.trialLabels, psth.trialLabels),
                                           axis=0)
        self.ntrials = self.ntrials + psth.ntrials

    def plot(self, i=None, ax=None, overlay=False):
        if ax is None:
            ax = gca()
        if not overlay:
            ax.clear()
        trialLabels = self.trialLabels[i]
        data = self.data[i, :]
        labels = np.unique(trialLabels)

        for li in range(len(labels)):
            label = labels[li]
            idx = trialLabels == label
            mu = data[idx, :].mean(0)
            sigma = data[idx, :].std(0)
            ax.plot(self.bins, mu)
            ax.fill_between(self.bins, mu-sigma, mu+sigma)
