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

class DirFiles(DPT.DPObject):
    """
    DirFiles(redoLevels=0, SaveLevels=0, objectLevel='Session')
    """
    def __init__(self, *args, **kwargs):
        # initialize fields in parent
        DPT.DPObject.__init__(self, *args, **kwargs)
        # check for files or directories in current directory
        dir_listing = os.listdir()
        # check number of items
        dnum = len(dir_listing)
        # create object if there are some items in this directory
        if dnum > 0:
            # update fields in parent
            self.dirs = os.getcwd()
            self.dir_list = dir_listing
            self.setidx = [0 for i in range(dnum)] 
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

## Custom hierarchy

It also possible to customize the hierarchy that DPT understands. This is done with a JSON coded config file. This is what 
the default config file looks like:

```json
{"subjects": {"pattern": "([a-zA-Z]+)","order":0},
  "subject": {"pattern": "([a-zA-Z]+)", "order": 1},
  "day": {"pattern": "([0-9]+)", "order": 2},
  "session": {"pattern": "(session)([a-z0-9]+)","order": 3},
  "array": {"pattern": "(array)([0-9]+)", "order": 4},
  "channel": {"pattern": "(channel)([0-9]+)", "order": 5},
  "cell": {"pattern": "(cell)([0-9]+)", "order": 6}
}
```

The main keys, e.g. 'subjects', 'subject', etc, represent the names of the different levels, while the `pattern` key within each level
specifies a regular expression for parsing that particular level. For example, the pattern for the `session` level is `(session)([a-z0-9]+)`,
which will match any string starting witn "session". Whatever comes after, e.g. "session01" or "sessioneye", will be used as an identifier for that session. Finally, the `order` key specifies the order of the level in the hierarchy. In the example, the level `subjects` is at the top of the hierarchy, i.e. it anchors all the other levels, while the level `cell` is at the bottom.
