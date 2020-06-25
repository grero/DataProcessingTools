# DataProcessingTools

[![Build Status](https://travis-ci.com/grero/DataProcessingTools.svg?branch=master)](https://travis-ci.com/grero/DataProcessingTools)
[![Coverage Status](https://coveralls.io/repos/github/grero/DataProcessingTools/badge.svg?branch=master)](https://coveralls.io/github/grero/DataProcessingTools?branch=master)

## Introduction
This package contains tools for navigating and managing a data organized in a hierarchical manner

## Usage

### Basic level operations
```python
import DataProcessingTools as DPT

cwd = "Pancake/20130923/session01/array01"

# Get the current level
ll = DPT.levels.level(cwd)

# Resolve the relative path from `cwd` to the `session` directory.
rr = DPT.levels.resolve_level("session", cwd)

# Find all e.g. cell directories under the current directory
celldirs = DPT.levels.get_level_dirs("cell", cwd)
```

### Objects
```python
import DataProcessingTools as DPT
spiketimes = np.cumsum(np.random.exponential(0.3, 100000))
trialidx = np.random.random_integers(0, 100, (100000, ))
trial_labels = np.random.random_integers(1, 9, (101, ))
bins = np.arange(0, 100.0, 2.0)
psth1 = DPT.psth.PSTH(spiketimes, trialidx, bins, trial_labels)
psth1.dirs = ["Pancake/20130923/session01/array01/channel001/cell01"]

spiketimes = np.cumsum(np.random.exponential(0.3, 100000))
trialidx = np.random.random_integers(0, 100, (100000, ))
psth2 = DPT.psth.PSTH(spiketimes, trialidx, bins, trial_labels)
psth2.dirs = ["Pancake/20130923/session01/array01/channel002/cell01"]

# Concatenate the two PSTH objects into a list for plotting
ppsth = DPT.objects.DPObjects([psth1, psth2])

# Plot the first PSTH
fig = ppsth.plot(0)

# Plot the second PSTH without overlay
ppsth.plot(1, overlay=False)

# Append psth2 to psth1, creating an object spanning mulitple sets
psth1.append(psth2)

# To access the data for the first cell in this compound object
cell_idx = psth1.getindex("cell")

# The above returns a function that gives the index into the object's data
# corresponding to the cell level.

# To  access the data related to the first cell, we can do this
cell1_data = psth1.data[cell_idx(0),:]

# If, on the other hand, we want to group the data by session, we could do

session_idx = psth1.getindex("session")
session1_data = psth1.data[session_idx(0),:]

# For this example, since we only have a single session, we would be looking
# at all the data.
```
### A complete example
Here is an example of how to compute raster and psth for a list for a list of
cells and step through plots of both using PanGUI

```python
import DataProcessingTools as DPT
import numpy as np
import os
import PanGUI

# change this to wherever you keep the data hierarchy
datadir = os.path.expanduser("~/Documents/workingMemory")

# get the trials for one session
with DPT.misc.CWD(os.path.join(datadir, "Whiskey/20200106/session02")):
    trials = DPT.trialstructures.WorkingMemoryTrials()

# get response trials
response_cue, ridx, _ = trials.get_timestamps("response_on")

# get error trials
failure, eidx, _ = trials.get_timestamps("failure")

#error trials with response cue
reidx = np.intersect1d(ridx, eidx)

# get stimulus onset of the error trials
stim_onset, identity, location = trials.get_stim(0, reidx)

#convert from seconds to ms
stim_onset = 1000*np.array(stim_onset)

# get all the cells for one session
with DPT.misc.CWD(os.path.join(datadir, "Whiskey/20200106/session02")):
    cells = DPT.levels.get_level_dirs("cell")

# gather rasters and PSTH for these cells, for the error trials
bins = np.arange(-300, 1000.0, 10)
with DPT.misc.CWD(cells[0]):
        raster = DPT.raster.Raster(-300.0, 1000.0, stim_onset)
        psth = DPT.psth.PSTH(bins, 10, raster.spiketimes, raster.trialidx, location)
for cell in cells[1:]:
    with DPT.misc.CWD(cell):
        praster = DPT.raster.Raster(-300.0, 1000.0, stim_onset)
        raster.append(praster)
        psth.append(DPT.psth.PSTH(bins, 10, praster.spiketimes, praster.trialidx, location))

app = PanGUI.create_window([raster, psth], cols=1, indexer="cell")
```
