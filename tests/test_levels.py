import DataProcessingTools as DPT
import tempfile
import os


def test_level():
    cwd = "Pancake/20130923/session01/array02/channel033"
    ll = DPT.levels.level(cwd)
    assert ll == "channel"

    rr = DPT.levels.resolve_level("session", cwd)
    assert rr == "./../.."

    rr = DPT.levels.resolve_level("channel", cwd)
    assert rr == "."

    tdir = os.path.join(tempfile.gettempdir(), "levels")
    if not os.path.isdir(tdir):
        os.makedirs(tdir)

    with DPT.misc.CWD(tdir):
        dir1 = "Pancake/20130923/session01/array02/channel033"
        dir2 = "Pancake/20130923/session01/array02/channel034"
        for d in [dir1, dir2]:
            if not os.path.isdir(d):
                os.makedirs(d)
        dirs = DPT.levels.get_level_dirs("channel", "Pancake/20130923/session01/array02")
        assert dirs[0] == "Pancake/20130923/session01/array02/channel033"
        assert dirs[1] == "Pancake/20130923/session01/array02/channel034"

        dirs = DPT.levels.get_level_dirs("session", "Pancake/20130923/session01/array02")
        assert dirs[0] == "Pancake/20130923/session01/array02/./../../session01"

        dirs = DPT.levels.get_level_dirs("array", "Pancake/20130923/session01/array02")
        assert dirs[0] == "Pancake/20130923/session01/array02/."

        chdirs = DPT.levels.get_level_dirs("channel")
        assert len(chdirs) == 2
        assert DPT.levels.normpath(chdirs[0]) == dir1
        assert DPT.levels.normpath(chdirs[1]) == dir2

        arraydirs = DPT.levels.get_level_dirs("array")
        assert len(arraydirs) == 1
        assert DPT.levels.normpath(arraydirs[0]) == "Pancake/20130923/session01/array02"

    dir1 = "Pancake/20130923/session01/array02/channel033"
    ln = DPT.levels.get_level_name("session", dir1)
    assert ln == "session01"

    level_path = DPT.levels.get_level_path("session", dir1)
    assert level_path == "Pancake/20130923/session01"

def test_shortnames():
    dir1 = "Pancake/20130923/session01/array02/channel033/cell01"
    aa = DPT.levels.get_shortname("subject", dir1)
    assert aa == "P"
    aa = DPT.levels.get_shortname("session", dir1)
    assert aa == "s01"
    aa = DPT.levels.get_shortname("array", dir1)
    assert aa == "a02"
    aa = DPT.levels.get_shortname("channel", dir1)
    assert aa == "g033"
    aa = DPT.levels.get_shortname("cell", dir1)
    assert aa == "c01"
    aa = DPT.levels.get_shortname("cell", dir1)

    pth = "/Volumes/Data/workingMemory/Pancake/20230923/session01"
    npth = DPT.levels.normpath(pth)
    assert npth == "Pancake/20230923/session01"

