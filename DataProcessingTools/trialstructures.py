from .objects import DPObject
from .levels import *
from .misc import *
import numpy as np
import os
import csv
import re


class TrialStructure(DPObject):
    def __init__(self):
        DPObject.__init__(self)
        self.events = []
        self.timestamps = []

    def get_timestamps(self, event_label):
        """
        Return the timestamps corresponding to the
        specified event.
        """
        idx = np.where(self.events == event_label)[0]
        return self.timestamps[idx]


class WorkingMemoryTrials(TrialStructure):
    filename = "event_markers.csv"
    level = "day"
    def __init__(self):
        TrialStructure.__init__(self)
        self.trialevents = {"session_start": "11000000",
                            "trial_start": "00000000",
                            "fix_start": "00000001",
                            "stimBlankStart": "00000011",
                            "delay_start": "00000100",
                            "response_on": "00000101",
                            "reward_on": "00000110",
                            "failure": "00000111",
                            "trial_end": "00100000",
                            "manual_reward_on": "00001000",
                            "stim_start": "00001111",
                            "reward_off ": "00000100",
                            "trial_start": "00000010",
                            "target_on": "10100000",
                            "target_off": "10000000",
                            "left_fixation": "00011101"}
        self.reverse_map = dict((v,k) for k,v in self.trialevents.items())
        self.load()

    def load(self):
        sessiondir = get_level_name("session")
        leveldir = resolve_level(self.level)
        tidx = -1
        stidx = -1
        self.trialidx = []
        self.stimidx = []
        with open(os.path.join(leveldir, self.filename), "r") as csvfile:
            data = csv.DictReader(csvfile)
            for row in data:
                word = row["words"]
                if word[:2] == "11":
                    idx = int(word[2:], 2)
                    event = "".join(("session", str(idx).zfill(2))) 
                elif (word[:2] == "10") or (word[:2] == "01"):
                    if word[:2] == "10":
                        stimid = 1
                    else:
                        stimid = 2
                    if word[2] == "1":
                        switch = "on"
                        stidx += 1
                    else:
                        switch = "off"
                    locidx = int(word[3:], 2)
                    event = "stimulus_{0}_{1}_{2}".format(switch, stimid, locidx)
                else:
                    event = self.reverse_map.get(word, None)

                if event is not None:
                    self.events.append(event)
                    self.timestamps.append(np.float(row["timestamps"]))
                    if event == "trial_start":
                        tidx += 1
                        stidx = -1
                    self.trialidx.append(tidx)
                    self.stimidx.append(stidx)

        if sessiondir: 
            # filter events to only those in the current session
            sidx0 = self.events.index(sessiondir)
            sid = int("".join([f for f in filter(str.isdigit, sessiondir)]))
            sid += 1 
            try:
                ssid = "".join(("session", str(sid).zfill(2)))
                sidx1 = self.events.index(ssid)
            except:
                sidx1 = len(self.events)
            self.events = np.array(self.events[sidx0:sidx1])
            self.timestamps = np.array(self.timestamps[sidx0:sidx1]) - self.timestamps[sidx0]
            self.trialidx = np.array(self.trialidx[sidx0:sidx1]) - self.trialidx[sidx0]
            self.stimidx = np.array(self.stimidx[sidx0:sidx1])
        else:
            self.events = np.array(self.events)
            self.timestamps = np.array(self.timestamps)
            self.trialidx = np.array(self.trialidx)
            self.stimidx = np.array(self.stimidx)

    def get_timestamps(self, event_label):
        """
        Return the timestamps of all events matching `event_label`. 
        Wildcard can be used as well, so that, for example, to find all 
        stimulus 1 onsets, regardless of position, use

        trials.get_timestamps("stimulus_on_1_*")

        """
        idx = np.zeros((len(self.events), ), dtype=np.bool)
        p = re.compile(event_label)
        for (i,ee) in enumerate(self.events):
            m = p.match(ee)
            if m is not None: 
                idx[i] = True
        
        return self.timestamps[idx], self.trialidx[idx], self.stimidx[idx]

    def get_stim(self, stimidx=0, trialidx=None):
        """
        Return the timestamp, identity and location of the stimulus
        at `stimidx` of every trial.
        """
        fidx = self.stimidx==stimidx
        if trialidx is not None:
            qidx = np.isin(self.trialidx, trialidx)
            fidx = fidx & qidx
        p = re.compile("stimulus_on_([0-9]+)_([0-9]+)")
        location = []
        identity = []
        timestamps = []
        for (ss,tt) in zip(self.events[fidx], self.timestamps[fidx]):
            m = p.match(ss)
            if m is not None:
                g = m.groups()
                identity.append(int(g[0]))
                location.append(int(g[1]))
                timestamps.append(tt)
        return timestamps, identity, location

def get_trials():
    """
    Attempt to auto-discover the trial structure by looking for a file
    corresponding to a known structure in the current working directory
    """
    for Trials in TrialStructure.__subclasses__():
            leveldir = resolve_level(Trials.level)
            with CWD(leveldir):
                if os.path.isfile(Trials.filename):
                    trials = Trials()
                    return trials
