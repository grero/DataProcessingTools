import numpy as np
from matplotlib.pyplot import gcf
from . objects import DPObject


class PSTH(DPObject):
    def __init__(self, spiketimes, trialidx, bins, triallabels=None):
        ntrials = trialidx.max()+1
        counts = np.zeros((ntrials, np.size(bins)))
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

    def plot(self, i=None, fig=None):
        if fig is None:
            fig = gcf()
        ax = fig.add_subplot(111)
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
