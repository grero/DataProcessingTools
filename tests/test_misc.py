import DataProcessingTools as DPT
import tempfile
import os


def test_basic():
    tempdir = tempfile.gettempdir()

    cwd = os.getcwd()
    with DPT.misc.CWD(tempdir):
        assert os.path.samefile(os.getcwd(), tempdir)
    assert os.path.samefile(os.getcwd(), cwd)


def test_procesDirs():    
    dirs = ["dir_{0}".format(i) for i in range(5)]

    @DPT.misc.processDirs(dirs)
    def testfunc():
        with open("test1.txt", "w") as ff:
            ff.write("sometest\n")

    tempdir = tempfile.gettempdir()
    with DPT.misc.CWD(tempdir):
        for d in dirs:
            if not os.path.isdir(d):
                os.mkdir(d)
        testfunc()
        allok = True
        for d in dirs:
            with DPT.misc.CWD(d):
                allok = allok and os.path.isfile("test1.txt")
                if allok:
                    os.remove("test1.txt")
            os.rmdir(d)
        assert allok

