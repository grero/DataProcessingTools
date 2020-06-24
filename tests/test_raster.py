import DataProcessingTools as DPT
import numpy as np
import tempfile
import os
import scipy.io as sio
import matplotlib.pylab as plt


def test_basic():

    spiketimes = np.array([0.1, 0.15, 0.3, 0.4, 0.5, 0.6,
                           1.1, 1.2, 1.3, 1.4, 2.5, 2.6])
    trial_events = np.array([0.1, 1.1])

    raster = DPT.raster.Raster(-0.1, 0.5, alignto=trial_events, spiketimes=spiketimes,
                               dirs=["session01/array01/channel001/cell01"])
    assert (raster.trialidx == [0, 0, 0, 0, 0, 1, 1, 1, 1]).all()
    assert np.isclose(raster.spiketimes, [0.0, 0.05, 0.2, 0.3, 0.4, 0.0, 0.1, 0.2, 0.3]).all()

    # test plotting
    fig = plt.figure()
    ax = fig.add_subplot(111)
    raster.plot(ax=ax)
    x, y = ax.lines[0].get_data()
    assert np.isclose(raster.spiketimes, x).all()
    assert np.isclose(raster.trialidx, y).all()

    raster.append(DPT.raster.Raster(-0.1, 0.5, alignto=trial_events, spiketimes=spiketimes,
                                   dirs=["session01/array01/channel002/cell01"]))
    cell_idx = raster.getindex("cell")
    for i in range(2):
        assert np.allclose(raster.spiketimes[cell_idx(i)], [0.0, 0.05, 0.2, 0.3, 0.4, 0.0, 0.1, 0.2, 0.3])
        assert (raster.trialidx[cell_idx(i)] == [0, 0, 0, 0, 0, 1, 1, 1, 1]).all()
