import DataProcessingTools as DPT
import tempfile
import os


def test_config():
    tdir = tempfile.gettempdir()
    with DPT.misc.CWD(tdir):
        levels = DPT.levels.levels
        level_patterns = DPT.levels.level_patterns_s
        DPT.levels.create_config(levels, level_patterns, "config.json")
        DPT.levels.update_config("config.json")
        assert DPT.levels.levels == levels
        assert DPT.levels.level_patterns_s == level_patterns


def test_level():
    ll = DPT.levels.level("sessioneye")
    assert ll == "session"

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

    aa = DPT.levels.get_shortname("session", "sessioneye")
    assert aa == "seye"

    aa = DPT.levels.get_numbers("session01")
    assert aa == "01"

def test_processLevel():
    tdir = tempfile.gettempdir()
    with DPT.misc.CWD(tdir):
        if not os.path.isdir("data2"):
            os.mkdir("data2")
        with DPT.misc.CWD("data2"):
            dir1 = "Pancake/20130923/session01/array02/channel033"
            dir2 = "Pancake/20130923/session01/array02/channel034"
            dir3 = "Pancake/20130923/session01/array02/channel035"
            for d in [dir1, dir2, dir3]:
                if not os.path.isdir(d):
                    os.makedirs(d)

            dirs, data = DPT.levels.processLevel("channel",
                                                 "x = 1; y = 2; data.append([x,y])",
                                                 exclude=["channel035"])

            assert len(dirs) == 2
            assert dirs[0] == dir1
            assert dirs[1] == dir2
            assert data == [[1, 2], [1, 2]]
            for d in [dir1, dir2, dir3]:
                os.removedirs(d)
        os.rmdir("data2")
