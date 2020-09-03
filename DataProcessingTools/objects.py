import numpy as np
import matplotlib.pylab as plt
import pickle
import hickle
import hashlib
from . import levels, misc
from .levels import normpath
import h5py
import os
import fnmatch
import pathlib


class ExclusiveOptions():
    def __init__(self, options, checked=None):
        self.options = options
        if checked is None:
            self.checked = 0
        else:
            self.checked = checked

    def select(self, option):
        if option in self.options:
            self.checked = self.options.index(option)

    def selected(self):
        return self.options[self.checked]


class DirCmd():
    """
    Run a command, appending the result to `data`
    """
    def __init__(self, cmd=None, **kwargs):
        data = []
        exec(cmd, {}, {"data": data})
        self.data = data
        self.dirs = [os.getcwd()]

    def append(self, obj):
        self.data.extend(obj.data)
        self.dirs.extend(obj.dirs)


class DPObject():
    argsList = []
    filename = ""
    level = None

    def __init__(self, *args, **kwargs):
        fname = kwargs.get("loadFrom", None)
        _dirs = kwargs.get("dirs")
        if fname is not None:
            self.load(fname=fname)
        else:
            if self.level is not None and _dirs != []:
                ldir = levels.resolve_level(self.level)
            else:
                ldir = os.getcwd()
            with misc.CWD(ldir):
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
                saveLevel = kwargs.get("saveLevel", 0)
                fname = self.get_filename()
                verbose = kwargs.get("verbose", 1)
                if redoLevel == 0 and os.path.isfile(fname):
                    self.load(fname)
                    if verbose > 0:
                        print("Object loaded from file {0}".format(fname))
                else:
                    # create object
                    self.create(*args, **kwargs)
                    if self.dirs and saveLevel > 0:
                        self.save()
                        if verbose > 0:
                            print("Object saved to file {0}".format(fname))

    def create(self, *args, **kwargs):
        self.dirs = kwargs.get("dirs", [os.getcwd()])
        self.setidx = []
        if self.dirs:
            normpath = kwargs.get("normpath", True)
            if normpath:
                self.dirs = [levels.normpath(d) for d in self.dirs]
            self.plotopts = {"indexer": self.level}
            self.indexer = self.getindex(self.level)
            self.current_idx = None
            if kwargs.get("verbose", 1):
                print("Object created")

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
            if isinstance(splotopts[k], ExclusiveOptions):
                for (kk, vv) in v.items():
                    if vv:
                        splotopts[k].select(kk)
                        replot = True
                        break
            elif isinstance(v, dict):
                self.update_plotopts(v, ax, self.plotopts[k])
            else:
                if v != splotopts[k]:
                    splotopts[k] = v
                    if k == "indexer":
                        self.update_index(v)
                    replot = True

        if replot:
            self.plot(self.current_idx, ax=ax)

    def __add__(self, obj):
        pass

    def update_idx(self, index):
        """
        Return `index` if it is valid for the current object
        """
        return max(0, min(index, self.data.shape[0]-1))

    def getlevels(self):
        """
        Return a list of levels that this object understands
        """
        _levels = []
        for d in self.dirs:
            for l in levels.levels:
                ln = levels.get_level_name(l, d)
                if ln:
                    if l not in _levels:
                        _levels.append(l)

        return _levels

    def getindex(self, level=None):
        """
        Return an index into this object for the requested level.
        """
        if level is None:
            return lambda i: np.where(np.array(self.setidx)==i)[0]

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

    def update_index(self, level):
        self.indexer = self.getindex(level)

    def append(self, obj):
        """
        Appends the data of `obj` to this object.
        """
        if self.setidx:
            mx = self.setidx[-1]+1
            for s in obj.setidx:
                self.setidx.append(s+mx)
        if self.dirs:
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
            elif k == "dirs":
                self.dirs = []
                for d in v:
                    self.dirs.append(str(pathlib.Path(d)))
            elif k == "indexer":
                pass
            else:
                setattr(self, k, v)

    def save(self, fname=None):
        if fname is None:
            fname = self.get_filename()
        tosave = {}
        for (k, v) in self.__dict__.items():
            if k != "indexer":
                tosave[k] = v
        hickle.dump(tosave, fname, mode="w")

    def hash(self):
        s = pickle.dumps(self.args)
        return hashlib.md5(s).hexdigest()[:4]

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


def processDirs(dirs=None, objtype=None, level=None, 
                getArgsList=False, exclude=[], objargs=[], 
                do_normpath=False, **kwargs):
    """
    Instantiates an object of type `objtype` in each directory in `dirs`,
    concatenating them into a single object that is then returned

    If `dirs` is `None`, all directories under the current directory will be visited.
    """
    if getArgsList:
        return {"dirs": None, "objtype": None,
                "level":None, "exclude": []}
    if dirs is None:
        if level is None:
            level = objtype.level
        dirs = levels.get_level_dirs(level)
    if not dirs:
        return objtype(dirs=[])

    outdirs = []
    pp = []
    cmd = kwargs.get("cmd")
    if cmd is not None and objtype is None:
        objtype = DirCmd
    for d in dirs:
        do_exclude = False
        for ed in exclude:
            do_exclude = fnmatch.fnmatch(d, ed)
            if do_exclude:
                break
        if not do_exclude:
            if do_normpath:
                outdirs.append(normpath(d))
            else:
                outdirs.append(d)

    ii = 0
    while ii < len(outdirs):
        with misc.CWD(outdirs[ii]):
            obj = objtype(*objargs, **kwargs)
            ii += 1
            if obj.dirs:
                break

    while ii < len(outdirs):
        with misc.CWD(outdirs[ii]):
            obj1 = objtype(*objargs, **kwargs)
            ii += 1
            if obj1.dirs:
                obj.append(obj1)

    return obj
