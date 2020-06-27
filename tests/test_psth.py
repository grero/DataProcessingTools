import numpy as np
import DataProcessingTools as DPT
import matplotlib.pylab as plt


def test_psth():
    spiketimes = np.cumsum(np.random.exponential(0.3, 100000))
    trialidx = np.random.random_integers(0, 100, (100000, ))
    trial_labels = np.random.random_integers(1, 9, (101, ))
    bins = np.arange(0, 100.0, 2.0)
    psth = DPT.psth.PSTH(bins, 1, spiketimes, trialidx, trial_labels,
                        dirs=["Pancake/20130923/session01/array01/channel001/cell01"])

    assert psth.data.shape[0] == 101

    idx = psth.update_idx(1)
    assert idx == 1

    idx = psth.update_idx(201)
    assert idx == 100

    psth.plot()
    fig = plt.gcf()
    assert len(fig.axes[0].lines) == 9

    # test update plotopts
    plotopts = {"group_by_label": False}
    psth.update_plotopts(plotopts,ax=fig.axes[0])
    assert len(fig.axes[0].lines) == 1

    spiketimes = np.cumsum(np.random.exponential(0.3, 100000))
    trialidx = np.random.random_integers(0, 100, (100000, ))

    psth2 = DPT.psth.PSTH(bins, 1, spiketimes, trialidx, trial_labels,
                         dirs= ["Pancake/20130923/session01/array01/channel002/cell01"])
    # test appending objects
    psth.append(psth2)

    assert psth.data.shape[0] == 202
    assert psth.trial_labels.shape[0] == 202
    assert len(psth.setidx) == 202

    idx = psth.getindex("cell")
    data = psth.data[idx(1), :]
    assert (data == psth2.data).all()

    idx = psth.getindex("session")
    data = psth.data[idx(0), :]
    assert (data == psth.data).all()

def test_sliding_psth():
    spiketimes = np.cumsum(np.random.exponential(0.3, 100000))
    trialidx = np.random.random_integers(0, 100, (100000, ))
    trial_labels = np.random.random_integers(1, 9, (101, ))
    bins = np.arange(0, 100.0, 2.0)
    psth = DPT.psth.PSTH(bins, 10, spiketimes, trialidx, trial_labels,
                        dirs=["Pancake/20130923/session01/array01/channel001/cell01"])
    assert psth.data.shape == (101, len(bins) - 10)
    assert psth.bins.shape == (len(bins) - 10, )
