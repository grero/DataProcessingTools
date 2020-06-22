import DataProcessingTools as DPT
import numpy as np

def test_basic():
    events = [("trial_start", 0.1),
              ("target_on", 0.2),
              ("target_off", 0.5),
              ("reward_on", 0.6),
              ("reward_off", 0.8),
              ("trial_end", 0.85),
              ("trial_start", 1.1),
              ("target_on", 1.2),
              ("target_off", 1.5),
              ("failure_on", 1.6),
              ("failure_off", 1.8),
              ("trial_end", 1.85)]

    trials = DPT.trialstructures.TrialStructure()
    trials.events = np.array([event[0] for event in events])
    trials.timestamps = np.array([event[1] for event in events])

    trial_starts = trials.get_timestamps("trial_start")
    assert (trial_starts == [0.1, 1.1]).all()

