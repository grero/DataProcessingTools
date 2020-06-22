import numpy as np
from matplotlib.pyplot import gcf
from .objects import DPObject
from . import levels
from .raster import Raster


class PSTH(DPObject):
    def __init__(self, bins, spiketimes=None, trialidx=None, triallabels=None,
                 trial_events=None):
        tmin = bins[0]
        tmax = bins[-1]
        if spiketimes is None:
            # attempt to load from the current directory
            raster = Raster(tmin, tmax, trial_event=trial_events)
            spiketimes = raster.spiketimes
            trialidx = raster.trialidx
            triallabels = raster.trial_labels
        ntrials = trialidx.max()+1
        counts = np.zeros((ntrials, np.size(bins)), dtype=np.int)
        for i in range(np.size(spiketimes)):
            jj = np.searchsorted(bins, spiketimes[i])
            if 0 <= jj < np.size(bins):
                counts[trialidx[i], jj] += 1
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

        # index to keep track of sets, e.g. trials
        self.setidx = [0 for i in range(self.ntrials)]

    def append(self, psth):
        if not (self.bins == psth.bins).all():
            ValueError("Incompatible bins")

        DPObject.append(self, psth)
        self.data = np.concatenate((self.data, psth.data), axis=0)
        self.trial_labels = np.concatenate((self.trial_labels, psth.trial_labels),
                                           axis=0)
        self.ntrials = self.ntrials + psth.ntrials

    def plot(self, i=None, fig=None, overlay=False):
        if fig is None:
            fig = gcf()
        ax = fig.add_subplot(111)
        if not overlay:
            ax.clear()
        labels = np.unique(self.trial_labels)
        if i is not None:
            # plot a particular label
            labels = labels[i:i+1]

        for li in range(len(labels)):
            label = labels[li]
            idx = self.trial_labels == label
            mu = self.data[idx, :].mean(0)
            sigma = self.data[idx, :].std(0)
            ax.plot(self.bins, mu)
            ax.fill_between(self.bins, mu-sigma, mu+sigma)
        return fig
