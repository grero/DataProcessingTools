import DataProcessingTools as DPT
import matplotlib.pylab as plt
import numpy as np
import tempfile
import os


class MyObj(DPT.objects.DPObject):
    argsList = ["bins"]
    filename = "myobj.hkl"
    level = "cell"

    def __init__(self,  *args, **kwargs):
        DPT.objects.DPObject.__init__(self, *args, **kwargs)
        for i in range(len(self.dirs)):
            self.setidx.extend([i for j in range(3)])
        self.plotopts = {"exponent": 1.0,
                         "color": DPT.objects.ExclusiveOptions(["blue","red"], 0)}

    def plot(self, i=None,  ax=None):
        if ax is None:
            ax = plt.gca()
        if not self.plotopts.get("overlay", False):
            ax.clear()
        color = self.plotopts["color"].selected()
        x = np.array([0, 1, 2, 3])
        y = x**self.plotopts["exponent"]
        ax.plot(x, y, color=color)

def test_plot():
    cwd = "Pancake/20130923/session01/array01/channel001/cell01"
    tempdir = tempfile.gettempdir()
    with DPT.misc.CWD(tempdir):
        os.makedirs(cwd)
        with DPT.misc.CWD(cwd):
            obj = MyObj([0.1, 0.2, 0.3], normpath=True, saveLevel=0)
            assert np.allclose(obj.args["bins"], [0.1, 0.2, 0.3])
            ax = plt.gca()
            ax.clear()
            obj.plot(ax=ax)
            x = np.array([0, 1, 2, 3])
            xy = ax.lines[0].get_data()
            assert np.allclose(xy[0], x)
            assert np.allclose(xy[1], x**1.0)
            obj.update_plotopts({"exponent": 2.0}, ax=ax)
            xy = ax.lines[0].get_data()
            assert np.allclose(xy[1], x**2.0)
            obj.update_plotopts({"color": {"red": True}}, ax=ax)
            assert ax.lines[0].get_color() == "red"

def test_append():
    tempdir = tempfile.gettempdir()
    dirs = ["Pancake/20130923/session01/array01/channel001/cell01",
            "Pancake/20130923/session01/array01/channel001/cell02",
            "Pancake/20130923/session01/array02/channel033/cell01",
            "Pancake/20130923/session01/array02/channel034/cell01"]

    tempdir = os.path.join(tempdir, "data")
    if not os.path.isdir(tempdir):
        os.makedirs(tempdir)

    with DPT.misc.CWD(tempdir):
        for d in dirs:
            if not os.path.isdir(d):
                os.makedirs(d)

        with DPT.misc.CWD(dirs[0]):
            obj1 = MyObj([0.1, 0.2, 0.3])
            h = obj1.hash()
            assert h == "c872"

        for d in dirs[1:]:
            with DPT.misc.CWD(d):
                obj = MyObj([0.1, 0.2, 0.3])
                obj1.append(obj)

        # do the same thing with processDirs
        obj3 = DPT.objects.processDirs(dirs=dirs, objtype=MyObj,
                                       objargs=[[0.1, 0.2, 0.3]])
        obj4 = DPT.objects.processDirs(objtype=MyObj,
                                       objargs=[[0.1, 0.2, 0.3]])
        obj5 = DPT.objects.processDirs(dirs=[], objtype=MyObj,
                                       objargs=[[0.1, 0.2, 0.3]])

    assert obj1.setidx == [0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3]
    assert obj3.setidx == obj1.setidx
    assert obj4.setidx == obj3.setidx
    assert obj5.setidx == []

    assert obj1.dirs == dirs
    assert obj1.dirs == obj3.dirs
    assert obj1.dirs == obj4.dirs
    assert obj5.dirs == []
    mylevels = obj1.getlevels()
    assert mylevels == ["subject", "day", "session","array","channel","cell"]

    # test trial
    idx = obj.getindex("trial")
    assert idx(0) == [0]

    idx = obj1.getindex("cell")
    assert (idx(0) == [0, 1, 2]).all()
    assert (idx(3) == [9, 10, 11]).all()
    assert len(idx(4)) == 0

    idx = obj1.getindex("channel")
    assert (idx(0) == [0, 1, 2, 3, 4, 5]).all()
    assert (idx(1) == [6, 7, 8]).all()
    assert (idx(2) == [9, 10, 11]).all()

    idx = obj1.getindex("array")
    assert (idx(0) == [0, 1, 2, 3, 4, 5]).all()
    assert (idx(1) == [6, 7, 8, 9, 10, 11]).all()

    idx = obj1.getindex(None)
    assert (idx(0) == [0, 1, 2]).all()

    assert obj.get_filename() == "myobj_c872.hkl"
    obj.save()
    assert os.path.isfile(obj.get_filename())
    obj7 = MyObj(loadFrom="myobj_c872.hkl")
    assert obj7.args["bins"] == obj.args["bins"]
    assert obj7.dirs == obj.dirs

    os.remove(obj.get_filename())

def test_object():

    class MyObj2(DPT.objects.DPObject):
        argsList = ["tmin", "tmax"]
        filename = "test.mat"
    
    tdir = tempfile.gettempdir()
    with DPT.misc.CWD(tdir):
        assert MyObj2.level is None
        obj = MyObj2(-0.1, 1.0, normpath=False, saveLevel=1)
        assert os.path.isfile(obj.get_filename())
        assert obj.args["tmin"] == -0.1
        assert obj.args["tmax"] == 1.0
        obj2 = MyObj2(-0.1, 1.0, normpath=False)
        assert obj2.args["tmin"] == obj.args["tmin"]
        assert obj2.args["tmax"] == obj.args["tmax"]
        os.unlink(obj.get_filename())


def test_empty():
    class MyObj3(DPT.objects.DPObject):
        argsList = ["tmin", "tmax"]
        filename = "test3.mat"

        def create(self, *args, **kwargs):
            self.dirs = []
            self.setidx = []

    obj = MyObj3(1.0, 0.1, normpath=False)
    # test that no object was saved
    assert not os.path.isfile("test3.mat")


def test_cmdobj():
    tdir = os.path.join(tempfile.gettempdir(), "testcmd")
    if not os.path.isdir(tdir):
        os.mkdir(tdir) 
    with DPT.misc.CWD(tdir):
        cmdobj1 = DPT.objects.DirCmd("data.append(1)")
        cmdobj2 = DPT.objects.DirCmd("data.append(2)")
        cmdobj1.append(cmdobj2)
        assert cmdobj1.data == [1, 2]

        dirs = ["array01/channel001", "array1/channel002","array01/channel003"]
        for d in dirs:
            if not os.path.isdir(d):
                os.makedirs(d)
        cmdobj_f = DPT.objects.processDirs(dirs=dirs,
                                           cmd="data.append(1)",
                                           exclude=["*array01/channel003"])
        cmdobj_p = DPT.objects.processDirs(level="channel",objtype= DPT.objects.DirCmd,
                                           cmd="data.append(1)",
                                           exclude=["*array01/channel003"])
        for d in dirs:
            os.removedirs(d)
        assert cmdobj_f.data == [1, 1]
        assert cmdobj_p.data == cmdobj_f.data
        assert len(cmdobj_p.dirs) == 2
        assert DPT.misc.issubpath(dirs[0], cmdobj_p.dirs[0])
        assert DPT.misc.issubpath(dirs[1], cmdobj_p.dirs[1])
        assert cmdobj_p.dirs == cmdobj_f.dirs
    os.rmdir(tdir)
    argslist = DPT.objects.processDirs(getArgsList=True)
    assert argslist == {"dirs": None, "objtype":None,
                        "level": None, "exclude": []}
