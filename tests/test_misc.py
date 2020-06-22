import DataProcessingTools as DPT
import tempfile
import os


def test_basic():
    tempdir = tempfile.gettempdir()

    cwd = os.getcwd()
    with DPT.misc.CWD(tempdir):
        assert os.path.samefile(os.getcwd(), tempdir)
    assert os.path.samefile(os.getcwd(), cwd)
