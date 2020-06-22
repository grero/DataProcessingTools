import DataProcessingTools as DPT
import numpy as np
import tempfile
import os
import scipy.io as sio


def test_basic():

    spiketimes = np.array([0.1, 0.15, 0.3, 0.4, 0.5, 0.6,
                           1.1, 1.2, 1.3, 1.4, 2.5, 2.6])
    trial_events = np.array([0.1, 1.1])

    raster = DPT.raster.Raster(-0.1, 0.5, trial_events, spiketimes)
    assert (raster.trialidx == [0, 0, 0, 0, 0, 1, 1, 1, 1]).all()
    assert np.isclose(raster.spiketimes, [0.0, 0.05, 0.2, 0.3, 0.4, 0.0, 0.1, 0.2, 0.3]).all()


def test_load():
    spiketimes = np.array([0.1, 0.15, 0.3, 0.4, 0.5, 0.6,
                           1.1, 1.2, 1.3, 1.4, 2.5, 2.6])
    trial_events = np.array([0.1, 1.1])

    tempdir = tempfile.gettempdir()
    with DPT.misc.CWD(tempdir):
        pth = "Pancake/20130923/session01/array01/channel001/cell01"
        if not os.path.isdir(pth):
            os.makedirs(pth)
        sio.savemat(os.path.join(pth, "unit.mat"), {"timestamps": spiketimes,
                                                    "spikeForm": [0]})
        with DPT.misc.CWD(pth):
            raster = DPT.raster.Raster(-0.1, 0.5, trial_events)
            assert (raster.trialidx == [0, 0, 0, 0, 0, 1, 1, 1, 1]).all()
            assert np.isclose(raster.spiketimes, [0.0, 0.05, 0.2, 0.3, 0.4, 0.0, 0.1, 0.2, 0.3]).all()
