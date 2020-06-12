# DataProcessingTools

[![Build Status](https://travis-ci.com/grero/DataProcessingTools.svg?branch=master)](https://travis-ci.com/grero/DataProcessingTools)
[![Coverage Status](https://coveralls.io/repos/github/grero/DataProcessingTools/badge.svg?branch=master)](https://coveralls.io/github/grero/DataProcessingTools?branch=master)

## Introduction
This package contains tools for navigating and managing a data organized in a hierarcical manner

## Usage

```python
import DataProcessingTools as DPT

cwd = "Pancake/20130923/session01/array01"
ll = DPT.levels.level(cwd)
```
