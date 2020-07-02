import numpy as np
import matplotlib.pylab as plt
import pickle
import hickle
import hashlib
from . import levels
import h5py
import os


class DPObject():
    argsList = []
    filename = ""

    def __init__(self, *args, **kwargs):
        self.dirs = [os.getcwd()]
        normpath = kwargs.get("normpath", True)
        if normpath:
            self.dirs = [levels.normpath(d) for d in self.dirs]
        self.setidx = []
        self.plotopts = {}
        self.current_idx = None
        self.args = {}
        # process positional arguments
        # TODO: We need to somehow consume these, ie. remove the processed ones
        pargs = [p for p in filter(lambda t: not isinstance(t, tuple), type(self).argsList)]
        qargs = pargs.copy()
        for (k, v) in zip(pargs, args):
            self.args[k] = v
            qargs.remove(k)
        # run the remaining throgh kwargs
        for k in qargs:
            if k in kwargs.keys():
                self.args[k] = kwargs[k]

        # process keyword arguments
        kargs = filter(lambda t: isinstance(t, tuple), type(self).argsList)
        for (k, v) in kargs:
            self.args[k] = kwargs.get(k, v)

        redoLevel = kwargs.get("redoLevel", 0)
        fname = self.get_filename()
        if redoLevel == 0 and os.path.isfile(fname):
            self.load(fname)
        else:
            # create object
            self.create(*args, **kwargs)

    def create(self, *args, **kwargs):
        pass

    def plot(self, i, ax=None):
        pass

    def update_plotopts(self, plotopts, ax=None, splotopts=None):
        """
        Update this objects plotopts with the specified plotopts,
        triggering a re-plot only if any option actually changed.
        """
        if splotopts is None:
            splotopts = self.plotopts

        if ax is None:
            ax = plt.gca()
        replot = False
        for (k, v) in plotopts.items():
            if isinstance(v, dict):
                self.update_plotopts(v, ax, self.plotopts[k])
            else:
                if v != splotopts[k]:
                    splotopts[k] = v
                    replot = True

        if replot:
            self.plot(self.current_idx, ax=ax)

    def __add__(self, obj):
        pass

    def level(self):
        pass

    def update_idx(self, index):
        """
        Return `index` if it is valid for the current object
        """
        return max(0, min(index, self.data.shape[0]-1))

    def getindex(self, level=None):
        """
        Return an index into this object for the requested level.
        """
        if level is None:
            return lambda i: None
        elif level == "trial":
            # `trial` is just a catch all for the lowest level
            return lambda i: [i] if 0 <= i < len(self.setidx) else []

        level_names = []
        for d in self.dirs:
            q = levels.get_level_path(level, d)
            level_names.append(q)

        unique_names = []
        for l in level_names:
            if l not in unique_names:
                unique_names.append(l)

        idx = np.zeros((len(self.setidx), ), dtype=np.int)
        for i in range(len(self.setidx)):
            idx[i] = unique_names.index(level_names[self.setidx[i]])

        def func(i):
            return np.where(idx == i)[0]

        return func

    def append(self, obj):
        """
        Appends the data of `obj` to this object.
        """
        mx = self.setidx[-1]+1
        for s in obj.setidx:
            self.setidx.append(s+mx)
        for d in obj.dirs:
            self.dirs.append(d)

    def get_filename(self):
        """
        Return the base filename with an argument hash
        appended
        """
        h = self.hash()
        fn, ext = os.path.splitext(self.filename)
        fname = self.filename.replace(ext, "_{0}{1}".format(h, ext))
        return fname

    def load(self, fname=None):
        if fname is None:
            fname = self.get_filename()
        data = hickle.load(fname)
        for (k, v) in data.items():
            if k == "args":
                self.args = v
            else:
                setattr(self, k, v)

    def save(self, fname=None):
        if fname is None:
            fname = self.get_filename()
        hickle.dump(self.__dict__, fname, mode="w")

    def hash(self):
        s = pickle.dumps(self.args)
        return hashlib.md5(s).hexdigest()

class DPObjects():
    def __init__(self, objects):
        self.objects = objects

    def __getitem__(self, key):
        return self.objects[key]

    def update_idx(self, index):
        return max(0, min(index, len(self.objects)-1))

    def append(self, item):
        self.objects.append(item)

    def plot(self, i, *args, **kwargs):
        j = self.update_idx(i)
        return self.objects[j].plot(*args, **kwargs)
