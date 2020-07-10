import os
import numpy as np
from pyedfread import edf, edfread
from .objects import DPObject
import matplotlib.pylab as plt


class EyelinkTrials(DPObject):
    filename = "eyelinktrials.hkl"
    level = "session"
    argsList = ["trialStartMarker", "trialEndMarker",
                "edfFile"]

    def __init__(self, *args, **kwargs):
        DPObject.__init__(self, *args, **kwargs)
        if kwargs.get("saveLevel", 0) > 0:
            self.save()

    def create(self, *args, **kwargs):
        if not os.path.isfile(self.args["edfFile"]):
            return self
        edffile = self.args["edfFile"]
        trialStart = self.args["trialStartMarker"]
        trialEnd = self.args["trialEndMarker"]
        messages, timestamps = edfread.read_messages(edffile)

        trialStarts = []
        trialEnds = []
        for ts, message in zip(timestamps, messages):
            m = message.decode().strip("\x00").replace(" ", "")
            if m == trialEnd:
                trialEnds.append(ts)
            elif m == trialStart:
                trialStarts.append(ts)

        trialEnds = np.array(trialEnds)
        trialStarts = np.array(trialStarts)
        D = trialEnds[None, :] - trialStarts[:, None]
        D[D < 0] = D.max()
        if len(trialStarts) < len(trialEnds):
            # match every trial start with its closest trial end
            idx = D.argmin(1)
            trialEnds = trialEnds[idx]
        elif len(trialStarts) > len(trialEnds):
            idx = D.argmin(0)
            trialStarts = trialStarts[idx]

        sample_size = ((trialEnds - trialStarts).astype(np.uint64)).sum()

        samples, events, messages = edf.pread(edffile)
        sample_time = samples["time"]
        # get sampling rate by comparing distance between timestamps
        sr = sample_time[1] - sample_time[0]
        if sr == 0:
            # 2 kHz, i.e. 2 timestamps per second
            sample_size = np.uint64(2*sample_size)
        gazex = np.zeros((sample_size,))
        gazey = np.zeros((sample_size,))
        trialidx = np.zeros((sample_size,), dtype=np.uint64)
        ssidx = 0
        offset = 0
        for (i, (start, end)) in enumerate(zip(trialStarts, trialEnds)):
            sidx = np.searchsorted(sample_time[ssidx:], start, side='let')
            eidx = np.searchsorted(sample_time[ssidx:], end, side='right')
            sidx += ssidx
            eidx += ssidx
            w = eidx - sidx
            ssidx = eidx+1
            gazex[offset:offset + w] = samples["gx_left"][sidx:eidx]
            gazey[offset:offset + w] = samples["gy_left"][sidx:eidx]
            trialidx[offset:offset + w] = i
            offset += w

        self.gazeX = gazex
        self.gazeY = gazey
        self.trialStart = trialStarts
        self.trialEnd = trialEnds
        self.trialIdx = trialidx
        self.setidx = [0 for i in range(len(self.trialIdx))]

    def append(self, obj):
        DPObject.append(self, obj)
        self.gazeX = np.concatenate((self.gazeX, obj.gazeX))
        self.gazeY = np.concatenate((self.gazeY, obj.gazeY))
        self.trialIdx = np.concatente((self.trialIdx, obj.trialIdx))
    
    def plot(self, i, ax=None, getNumEvents=False, getPlotOpts=False, **kwargs):
        plotopts = {"level": "trial", "removeInvalid": True,
                    "overlay": False}
        if getPlotOpts:
            return plotopts
        if getNumEvents:
            if plotopts["level"] == "trial":
                return self.trialIdx.max()+1, i

        for (k, v) in plotopts.items():
            plotopts[k] = kwargs.get(k, v)

        if ax is None:
            ax = plt.gca()
        if not plotopts["overlay"]:
            ax.clear()
        if plotopts["level"] == "trial":
            idx = np.where(self.trialIdx == i)
            x = self.gazeX[idx]
            y = self.gazeY[idx]
            if plotopts["removeInvalid"]:
                x[x >= 1e8] = np.nan
                y[y >= 1e8] = np.nan
            ax.plot(x)
            ax.plot(y)
