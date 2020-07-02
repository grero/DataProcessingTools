import DataProcessingTools as DPT
import matplotlib.pylab as plt
import numpy as np
import tempfile
import os


class MyObj(DPT.objects.DPObject):
    argsList = ["bins"]
    filename = "myobj.hkl"

    def __init__(self,  *args, **kwargs):
        DPT.objects.DPObject.__init__(self, *args, **kwargs)
        for i in range(len(self.dirs)):
            self.setidx.extend([i for j in range(3)])
        self.plotopts = {"exponent": 1.0}

    def plot(self, i=None,  ax=None):
        if ax is None:
            ax = plt.gca()
        if not self.plotopts.get("overlay", False):
            ax.clear()
        x = np.array([0, 1, 2, 3])
        y = x**self.plotopts["exponent"]
        ax.plot(x, y)

def test_plot():
    obj = MyObj([0.1, 0.2, 0.3], normpath=False)
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

def test_append():
    tempdir = tempfile.gettempdir()
    dirs = ["Pancake/20130923/session01/array01/channel001/cell01",
            "Pancake/20130923/session01/array01/channel001/cell02",
            "Pancake/20130923/session01/array02/channel033/cell01",
            "Pancake/20130923/session01/array02/channel034/cell01"]

    with DPT.misc.CWD(tempdir):
        for d in dirs:
            if not os.path.isdir(d):
                os.makedirs(d)

        with DPT.misc.CWD(dirs[0]):
            obj1 = MyObj([0.1, 0.2, 0.3])
            h = obj1.hash()
            assert h == "c8720126006af0f987d71347a63e77bc"

        for d in dirs[1:]:
            with DPT.misc.CWD(d):
                obj = MyObj([0.1, 0.2, 0.3])
                obj1.append(obj)

    assert obj1.setidx == [0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3]
    assert obj1.dirs == dirs

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
    assert idx(0) is None

    assert obj.get_filename() == "myobj_c8720126006af0f987d71347a63e77bc.hkl"
    obj.save()
    assert os.path.isfile(obj.get_filename())
    os.remove(obj.get_filename())

def test_object():

    class MyObj2(DPT.objects.DPObject):
        argsList = ["tmin", "tmax"]
        filename = "test.mat"

    obj = MyObj2(-0.1, 1.0, normpath=False)

    assert obj.args["tmin"] == -0.1
    assert obj.args["tmax"] == 1.0

