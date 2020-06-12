import DataProcessingTools as DPT


def test_level():
    cwd = "Pancake/20130923/session01/array02/channel33"
    ll = DPT.levels.level(cwd)
    assert ll == "channel"

    rr = DPT.levels.resolve_level("session", cwd)
    assert rr == "./../../.."
