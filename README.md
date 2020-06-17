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
