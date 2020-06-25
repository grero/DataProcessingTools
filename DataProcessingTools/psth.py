import numpy as np
from matplotlib.pyplot import gcf, gca
from .objects import DPObject
from . import levels
from .raster import Raster
import os


class PSTH(DPObject):
    def __init__(self, bins, windowsize=1, spiketimes=None, trialidx=None, triallabels=None,
                 alignto=None, trial_event=None, dirs=None):
        DPObject.__init__(self)
        tmin = bins[0]
        tmax = bins[-1]
        if spiketimes is None:
            # attempt to load from the current directory
            raster = Raster(tmin, tmax, alignto=alignto, trial_event=trial_event)
            spiketimes = raster.spiketimes
            trialidx = raster.trialidx
            triallabels = raster.trial_labels
        ntrials = trialidx.max()+1
        counts = np.zeros((ntrials, np.size(bins)), dtype=np.int)
        for i in range(np.size(spiketimes)):
            jj = np.searchsorted(bins, spiketimes[i])
            if 0 <= jj < np.size(bins):
                counts[trialidx[i], jj] += 1

        self.windowsize = windowsize
        if windowsize > 1:
            scounts = np.zeros((ntrials, len(bins)-windowsize))
            for i in range(ntrials):
                for j in range(len(bins)-windowsize):
                    scounts[i, j] = counts[i, j:j+windowsize].sum()

            self.data = scounts
            self.bins = bins[:-windowsize]
        else:
            self.data = counts
            self.bins = bins

        self.ntrials = ntrials
        if triallabels is None:
            self.trial_labels = np.ones((ntrials,))
        elif np.size(triallabels) == ntrials:
            self.trial_labels = triallabels
        elif np.size(triallabels) == np.size(spiketimes):
            dd = {}
            for t, l in zip(trialidx, triallabels):
                dd[t] = l
            self.trial_labels = np.array([dd[t] for t in range(ntrials)])
        else:
            self.trial_labels = triallabels

        # index to keep track of sets, e.g. trials
        self.setidx = [0 for i in range(self.ntrials)]
        if dirs is not None:
            self.dirs = dirs
        else:
            self.dirs = [os.getcwd()]
        
        self.plotopts = {"group_by_label": True}
        self.current_idx = None

    def append(self, psth):
        if not (self.bins == psth.bins).all():
            ValueError("Incompatible bins")

        DPObject.append(self, psth)
        self.data = np.concatenate((self.data, psth.data), axis=0)
        self.trial_labels = np.concatenate((self.trial_labels, psth.trial_labels),
                                           axis=0)
        self.ntrials = self.ntrials + psth.ntrials

    def update_plotopts(self, plotopts, ax=None):
        if ax is None:
            ax = gca()
        if plotopts["group_by_label"] != self.plotopts["group_by_label"]:
            # re-plot
            self.plotopts["group_by_label"] = plotopts["group_by_label"]
            self.plot(self.current_idx, ax)

    def plot(self, i=None, ax=None, overlay=False):
        self.current_idx = i
        if ax is None:
            ax = gca()
        if not overlay:
            ax.clear()
        trial_labels = self.trial_labels[i]
        data = self.data[i, :]
        labels = np.unique(trial_labels)
        if self.plotopts["group_by_label"]:
            for li in range(len(labels)):
                label = labels[li]
                idx = trial_labels == label
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

