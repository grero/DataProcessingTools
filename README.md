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
ll = DPT.levels.level(cwd)

rr = DPHT.resolve_level("session", cwd)
```

### Objects
```python
import DataProcessingTools as DPT
spiketimes = np.cumsum(np.random.exponential(0.3, 100000))
trialidx = np.random.random_integers(0, 100, (100000, ))
trial_labels = np.random.random_integers(1, 9, (101, ))
bins = np.arange(0, 100.0, 2.0)
psth1 = DPT.psth.PSTH(spiketimes, trialidx, bins, trial_labels)

spiketimes = np.cumsum(np.random.exponential(0.3, 100000))
trialidx = np.random.random_integers(0, 100, (100000, ))
psth2 = DPT.psth.PSTH(spiketimes, trialidx, bins, trial_labels)

# Concatenate the two PSTH objects into a list
ppsth = DPT.objects.DPObjects([psth1, psth2])

# Plot the first PSTH
fig = ppsth.plot(0)

#Plot the second PSTH without overlay
ppsth.plot(1, overlay=False)
```

