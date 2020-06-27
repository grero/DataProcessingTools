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
    filename = "psth.mat"

    def __init__(self, bins, windowsize=1, spiketimes=None, trialidx=None, triallabels=None,
                 alignto=None, trial_event=None, dirs=None, redolevel=0, savelevel=1):
        DPObject.__init__(self)
        self.args = {"bins": bins, "windowsize": windowsize,
                     "alignto": alignto}
        fname = self.get_filename()
        if redolevel == 0 and os.path.isfile(fname):
            self.load(fname)
        else:
            # create object
            self.create(bins, windowsize, spiketimes, trialidx, triallabels,
                        alignto, trial_event, dirs, savelevel)

    def get_filename(self):
        """
        Return the base filename with an argument hash
        appended
        """
        h = self.hash()
        fname = self.filename.replace(".mat", "_{0}.mat".format(h))
        return fname

    def create(self, bins, windowsize=1, spiketimes=None, trialidx=None, triallabels=None,
                      alignto=None, trial_event=None, dirs=None, savelevel=1):
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
        
        if savelevel > 0:
            self.save()

    def load(self, fname=None):
        if fname is None:
            fname = self.filename
        with h5py.File(fname) as ff:
            args = {}
            for (k,v) in ff["args"].items():
                self.args[k] = v
            self.data = ff["counts"][:]
            self.ntrials = self.data.shape[0]
            self.bins = self.args["bins"][:self.data.shape[-1]]
            self.trial_labels = ff["trial_labels"][:]
            self.dirs = [s.decode() for s in ff["dirs"][:]]
            self.setidx = ff["setidx"][:].tolist()

    def hash(self):
        """
        Returns a hash representation of this object's arguments.
        """
        h = hashlib.sha1()
        for (k, v) in self.args.items():
            x = np.atleast_1d(v)
            h.update(x.tobytes())
        h.hexdigest()

    def save(self, fname=None):
        if fname is None:
            fname = self.get_filename()

        with h5py.File(fname, "w") as ff:
            args = ff.create_group("args")
            args["bins"] = self.args["bins"]
            args["windowsize"] = self.args["windowsize"]
            if self.args["alignto"] is not None:
                args["alignto"] = self.args["alignto"]
            ff["counts"] = self.data
            ff["trial_labels"] = self.trial_labels
            ff["dirs"] = np.array(self.dirs, dtype='S256')
            ff["setidx"] = self.setidx

    def append(self, psth):
        if not (self.bins == psth.bins).all():
            ValueError("Incompatible bins")

        DPObject.append(self, psth)
        self.data = np.concatenate((self.data, psth.data), axis=0)
        self.trial_labels = np.concatenate((self.trial_labels, psth.trial_labels),
                                           axis=0)
        self.ntrials = self.ntrials + psth.ntrials

    def plot(self, i=None, ax=None, overlay=False):
        if ax is None:
            ax = gca()
        if not overlay:
            ax.clear()
        trial_labels = self.trial_labels[i]
        data = self.data[i, :]
        labels = np.unique(trial_labels)

        for li in range(len(labels)):
            label = labels[li]
            idx = trial_labels == label
            mu = data[idx, :].mean(0)
            sigma = data[idx, :].std(0)
            ax.plot(self.bins, mu)
            ax.fill_between(self.bins, mu-sigma, mu+sigma)
