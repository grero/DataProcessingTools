import DataProcessingTools as DPT


class MyObj(DPT.objects.DPObject):
    def __init__(self, dirs, *args, **kwargs):
        DPT.objects.DPObject.__init__(self, *args, **kwargs)
        self.dirs = dirs
        for i in range(len(dirs)):
            self.setidx.extend([i for j in range(3)])


def test_level_idx():
    obj = MyObj(dirs=["session01/array01/channel01/cell01",
                      "session01/array01/channel01/cell02"])

    # test cell level
    idx = obj.getindex("cell")
    assert (idx(0) == [0, 1, 2]).all()
    assert (idx(1) == [3, 4, 5]).all()

    # test session level
    idx = obj.getindex("session")
    assert (idx(0) == [0, 1, 2, 3, 4, 5]).all()


def test_append():

    obj1 = MyObj(dirs=["session01/array01/channel001/cell01",
                        "session01/array01/channel001/cell02"])

    obj2 = MyObj(dirs=["session01/array02/channel033/cell01",
                         "session01/array02/channel034/cell01"])

    obj1.append(obj2)

    assert obj1.setidx == [0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3]
    assert obj1.dirs == ["session01/array01/channel001/cell01",
                         "session01/array01/channel001/cell02",
                         "session01/array02/channel033/cell01",
                         "session01/array02/channel034/cell01"]

    idx = obj1.getindex("cell")
    assert (idx(0) == [0, 1, 2]).all()
    assert (idx(3) == [9, 10, 11]).all()
    assert len(idx(4)) == 0

    idx = obj1.getindex("channel")
    assert (idx(0) == [0, 1, 2, 3, 4, 5]).all()
    assert (idx(1) == [6, 7, 8]).all()
    assert (idx(2) == [9, 10, 11]).all()

    idx = obj1.getindex(None)
    assert idx(0) is None


def test_object():

    class MyObj2(DPT.objects.DPObject):
        argsList = ["tmin", "tmax"]
        filename = "test.mat"

    obj = MyObj2(-0.1, 1.0)

    assert obj.args["tmin"] == -0.1
    assert obj.args["tmax"] == 1.0
    
