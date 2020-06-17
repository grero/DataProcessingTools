import numpy as np
import DataProcessingTools as DPT


def test_psth():
    spiketimes = np.cumsum(np.random.exponential(0.3, 100000))
    trialidx = np.random.random_integers(0, 100, (100000, ))
    trial_labels = np.random.random_integers(1, 9, (101, ))
    bins = np.arange(0, 100.0, 2.0)
    psth = DPT.psth.PSTH(spiketimes, trialidx, bins, trial_labels)
    psth.dirs = ["Pancake/20130923/session01/array01/channel001/cell01"]

    assert psth.data.shape[0] == 101

    idx = psth.update_idx(1)
    assert idx == 1

    idx = psth.update_idx(201)
    assert idx == 100

    fig = psth.plot()
    assert len(fig.axes[0].lines) == 9

    spiketimes = np.cumsum(np.random.exponential(0.3, 100000))
    trialidx = np.random.random_integers(0, 100, (100000, ))

    psth2 = DPT.psth.PSTH(spiketimes, trialidx, bins, trial_labels)
    psth2.dirs = ["Pancake/20130923/session01/array01/channel002/cell01"]
    ppsth = DPT.objects.DPObjects([psth])
    ppsth.append(psth2)
    assert ppsth[0] == psth
    assert ppsth[1] == psth2

    fig = ppsth.plot(0)
    assert len(fig.axes[0].lines) == 9
    ppsth.plot(1, fig=fig)
    assert len(fig.axes[0].lines) == 9

    ppsth.plot(0, fig=fig, overlay=True)
    assert len(fig.axes[0].lines) == 18

    # test appending objects
    psth.append(psth2)

    assert psth.data.shape[0] == 202
    assert psth.trial_labels.shape[0] == 202
    assert len(psth.setidx) == 202

    idx = psth.getindex("cell")
    data = psth.data[idx == 1, :]
    assert (data == psth2.data).all()
