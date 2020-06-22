import os


class CWD(object):
    def __init__(self, cwd):
        self.cwd = cwd
        self.pwd = os.getcwd()
        os.chdir(cwd)

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        os.chdir(self.pwd)
