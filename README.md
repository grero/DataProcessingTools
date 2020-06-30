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

# get all the cells for one session
with DPT.misc.CWD(os.path.join(datadir, "Whiskey/20200106/session02")):
    cells = DPT.levels.get_level_dirs("cell")

# gather rasters and PSTH for these cells, for the error trials
bins = np.arange(-300, 1000.0, 10)
with DPT.misc.CWD(cells[0]):
    raster = DPT.raster.Raster(-300.0, 1000.0, "stimulus1", "reward_on", "stimulus1",
                               redoLevel=1, saveLevel=0)
    psth = DPT.psth.PSTH(bins, 10, trialEvent="stimulus1", sortBy="stimulus1", trialType="reward_on",
                         redoLevel=1, saveLevel=0)
for cell in cells[1:]:
    with DPT.misc.CWD(cell):
        praster = DPT.raster.Raster(-300.0, 1000.0, "stimulus1", "reward_on", "stimulus1",
                                    redoLevel=1, saveLevel=0)
        raster.append(praster)
        ppsth = DPT.psth.PSTH(bins, 10, trialEvent="stimulus1", sortBy="stimulus1", trialType="reward_on",
                              redoLevel=1, saveLevel=0)
        psth.append(ppsth)

app = PanGUI.create_window([raster, psth], cols=1, indexer="cell")
```
