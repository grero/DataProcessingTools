import DataProcessingTools as DPT


def test_level_idx():
    obj = DPT.objects.DPObject()
    obj.dirs = ["session01/array01/channel01/cell01",
                "session01/array01/channel01/cell02"]
    obj.setidx = [0, 0, 0, 1, 1, 1]

    # test cell level
    idx = obj.getindex("cell")
    assert (idx == [0, 0, 0, 1, 1, 1]).all()

    # test session level
    idx = obj.getindex("session")
    assert (idx == [0, 0, 0, 0, 0, 0]).all()


def test_append():
    obj1 = DPT.objects.DPObject()
    obj1.dirs = ["session01/array01/channel001/cell01",
                 "session01/array01/channel001/cell02"]
    obj1.setidx = [0, 0, 0, 1, 1, 1]

    obj2 = DPT.objects.DPObject()
    obj2.dirs = ["session01/array02/channel033/cell01",
                 "session01/array02/channel034/cell01"]
    obj2.setidx = [0, 0, 0, 1, 1, 1]

    obj1.append(obj2)

    assert obj1.setidx == [0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3]
    assert obj1.dirs == ["session01/array01/channel001/cell01", 
                         "session01/array01/channel001/cell02",
                         "session01/array02/channel033/cell01",
                         "session01/array02/channel034/cell01"]
