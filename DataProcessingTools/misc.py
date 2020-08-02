import os
import functools


class CWD(object):
    def __init__(self, cwd):
        self.cwd = cwd
        self.pwd = os.getcwd()
        os.chdir(cwd)

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        os.chdir(self.pwd)

def processDirs(dirs):
    """
    Calls `func` for every directory in `dirs`

    ## Examples
    ```python
    @processDirs(dirs)
    def createObj():
        obj = Obj()
    ```
    """
    def decorate_func(func):
        @functools.wraps(func)
        def wrapper_processDirs(*args,**kwargs):
            for d in dirs:
                with CWD(d):
                    func(*args, **kwargs)
        return wrapper_processDirs
    return decorate_func
