import DataProcessingTools as DPT
from DataProcessingTools.trialstructures import WorkingMemoryTrials
import tempfile
import os
import numpy as np
import scipy.io as sio
import csv
import matplotlib.pylab as plt


def test_load():
    spiketimes = 1000*np.array([0.1, 0.15, 0.3, 0.4, 0.5, 0.6,
                                1.1, 1.2, 1.3, 1.4, 2.5, 2.6])
    trialEvents = [("11000001", 0.0),
                   (WorkingMemoryTrials.trialevents["trial_start"], 0.05),
                   ("10100001", 0.1),
                   ("10000001", 0.2),
                   ("01100001", 0.1),
                   ("01000001", 0.2),
                   (WorkingMemoryTrials.trialevents["response_on"], 0.3),
                   (WorkingMemoryTrials.trialevents["reward_on"], 0.4),
                   (WorkingMemoryTrials.trialevents["reward_off"], 0.5),
                   (WorkingMemoryTrials.trialevents["trial_end"], 0.6),
                   (WorkingMemoryTrials.trialevents["trial_start"], 1.0),
                   ("10100001", 1.1),
                   ("10000001", 1.2),
                   ("01100001", 1.1),
                   ("01000001", 1.2),
                   (WorkingMemoryTrials.trialevents["response_on"], 1.3),
                   (WorkingMemoryTrials.trialevents["reward_on"], 1.4),
                   (WorkingMemoryTrials.trialevents["reward_off"], 1.5),
                   (WorkingMemoryTrials.trialevents["trial_end"], 1.6)]

    tempdir = tempfile.gettempdir()
    with DPT.misc.CWD(tempdir):
        pth = "Pancake/20130923/session01/array01/channel001"
        for cell in ["cell01", "cell02"]:
            if not os.path.isdir(os.path.join(pth, cell)):
                os.makedirs(os.path.join(pth, cell))
            sio.savemat(os.path.join(pth, cell, "unit.mat"), {"timestamps": spiketimes,
                                                                  "spikeForm": [0.0]})
        
        with DPT.misc.CWD(os.path.join(pth, "cell01")):
            with DPT.misc.CWD(DPT.levels.resolve_level("day")):
                # save trial info
                with open("event_markers.csv", "w") as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(["words", "timestamps"])
                    for ee in trialEvents:
                        writer.writerow(ee)
                trials = DPT.trialstructures.get_trials()
                assert len(trials.events) == len(trialEvents)

            trials = DPT.trialstructures.get_trials()
            assert len(trials.events) == len(trialEvents)
            stim_onset, tidx, sidx = trials.get_timestamps("stimulus_on_1_*")
            assert (stim_onset == [0.1, 1.1]).all()
            spiketrain = DPT.spiketrain.Spiketrain()
            assert np.allclose(spiketrain.timestamps, spiketimes)
            raster = DPT.raster.Raster(-100.0, 500.0, "stimulus1", "reward_on", "stimulus1",
                                       redoLevel=1, saveLevel=0)
            assert (raster.trialidx == [0, 0, 0, 0, 0, 1, 1, 1, 1]).all()
            assert np.isclose(raster.spiketimes, [0., 50., 200., 300., 400., 0., 100., 200., 300.]).all()
            raster2 = DPT.raster.Raster(-100.0, 500.0, "stimulus2", "reward_on", "stimulus2",
                                       redoLevel=1, saveLevel=0)
            assert (raster2.trialidx == [0, 0, 0, 0, 0, 1, 1, 1, 1]).all()
            assert np.isclose(raster2.spiketimes, [0., 50., 200., 300., 400., 0., 100., 200., 300.]).all()
            raster3 = DPT.raster.Raster(-100.0, 500.0, "reward_on", "reward_on", "stimulus2",
                                       redoLevel=1, saveLevel=0)
            assert (raster3.trialidx == [0, 0, 0, 1]).all()
            psth = DPT.psth.PSTH([-100., 200., 400., 600.], 1, trialEvent="stimulus1",
                                                               sortBy="stimulus1",
                                                               trialType="reward_on",
                                                               redoLevel=1, saveLevel=0)
            assert psth.data.shape == (2, 4)
            assert (psth.data[0, :] == [0, 3, 2, 1]).all()
            assert (psth.data[1, :] == [0, 3, 1, 0]).all()

        with DPT.misc.CWD(os.path.join(pth, "cell02")):
            raster2 = DPT.raster.Raster(-100.0, 500.0, "stimulus1", "reward_on", "stimulus1",
                                        redoLevel=1, saveLevel=0)
            psth2 = DPT.psth.PSTH([-100., 200., 400., 600.], 1, trialEvent="stimulus1",
                                                               sortBy="stimulus1",
                                                               trialType="reward_on",
                                                               redoLevel=1, saveLevel=0)
        raster.append(raster2)
        cellidx = raster.getindex("cell")
        assert len(cellidx(1)) == len(raster2.setidx)
        raster.plot(cellidx(0))
        xy = plt.gca().lines[0].get_data()
        assert np.allclose(xy[1], raster.trialidx[cellidx(0)])
        psth.append(psth2)
        cellidx = psth.getindex("cell")
        assert len(cellidx(1)) == len(psth2.setidx)
        psth.plot(cellidx(0))
        assert len(plt.gca().lines) == 1
        os.remove(os.path.join(pth, "cell01", "unit.mat"))
        os.remove(os.path.join(pth, "cell02", "unit.mat"))
        os.rmdir("Pancake/20130923/session01/array01/channel001/cell01")
        os.rmdir("Pancake/20130923/session01/array01/channel001/cell02")
        os.rmdir("Pancake/20130923/session01/array01/channel001")
        os.rmdir("Pancake/20130923/session01/array01")
