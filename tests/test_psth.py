import numpy as np
import DataProcessingTools as DPT


def test_psth():
    spiketimes = np.cumsum(np.random.exponential(0.3, 100000))
    trialidx = np.random.random_integers(0, 100, (100000, ))
    trial_labels = np.random.random_integers(1, 9, (101, ))
    bins = np.arange(0, 100.0, 2.0)
    psth = DPT.psth.PSTH(spiketimes, trialidx, bins, trial_labels)

    assert psth.data.shape[0] == 101

    idx = psth.update_idx(1)
    assert idx == 1

    idx = psth.update_idx(201)
    assert idx == 100
