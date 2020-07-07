import os
import glob
import re

levels = ['subjects', 'subject', 'day', 'session', 'array', 'channel','cell']
level_patterns_s = ["*", "*", "[0-9]*", "session[0-9]*", "array[0-9]*", "channel[0-9]*", "cell[0-9]*"]

def get_numbers(ss):
    return "".join(filter(str.isdigit, ss))

shortnames = {"subjects": lambda x: "",
              "subject": lambda x: x[0],
              "day": lambda x: x,
              "session": lambda x: "s{0}".format(get_numbers(x)),
              "array": lambda x: "a{0}".format(get_numbers(x)),
              "channel": lambda x: "g{0}".format(get_numbers(x)),
              "cell": lambda x: "c{0}".format(get_numbers(x))}


def get_shortname(level, cwd =None):
    level_name = get_level_name(level, cwd)
    return shortnames[level](level_name)

def level(cwd=None):
    if cwd is None:
        cwd = os.get_cwd()
    """
    Return the level corresponding to the folder `cwd`.
    """
    pp = cwd.split(os.sep)[-1]
    ll = ''
    if pp.isdigit():
        ll = 'day'
    else:
        numstr = [str(i) for i in range(10)]
        ll = pp.strip(''.join(numstr))
    return ll


def resolve_level(target_level, cwd=None):
    """
    Return the relative path from `cwd` to the folder correpsonding
    to `target_level`
    """
    if cwd is None:
        cwd = os.getcwd()
    this_level = level(cwd)
    this_idx = levels.index(this_level)
    target_idx = levels.index(target_level)
    pl = ["."]
    for i in range(0, this_idx - target_idx):
        pl.append("..")
    return os.path.join(*pl)


def get_level_dirs(target_level, cwd=None):
    """
    Get the directories representing `target_level` under the directory
    pointed to by `cwd`.
    """
    if cwd is None:
        cwd = os.getcwd()
    target_idx = levels.index(target_level)
    this_level = level(cwd)
    if this_level in levels:
        this_idx = levels.index(this_level)
    else:
        # we are outside the hierarchy; use os.walk
        dirs = []
        pattern = re.compile(level_patterns_s[target_idx])
        for dpath, dnames, fnames in os.walk(cwd):
            for _dnames in dnames:
                m = pattern.match(_dnames)
                if m:
                    dirs.append(os.path.join(dpath, _dnames))
        dirs.sort()
        return dirs

    if target_idx == this_idx:
        dirs = [os.path.join(cwd, ".")]
    elif target_idx < this_idx:
        rel_path = resolve_level(target_level, cwd)
        pattern = level_patterns_s[target_idx]
        gpattern = os.path.join(cwd, rel_path, "..", pattern)
        dirs = sorted(glob.glob(gpattern))
    else:
        patterns = level_patterns_s[this_idx+1:target_idx+1]
        dirs = sorted(glob.glob(os.path.join(cwd, *patterns)))
    return dirs


def get_level_name(target_level, cwd=None):
    """
    Return the name of the requested level
    """
    if cwd is None:
        cwd = os.getcwd()

    this_level = level(cwd)
    this_idx = levels.index(this_level)
    target_idx = levels.index(target_level)
    i = this_idx
    cw = cwd
    pp = ""
    while i >= target_idx:
        cw, pp = os.path.split(cw)
        i -= 1
    return pp

def get_level_path(target_level, cwd=None):
    """
    Return the full path to requested level
    """
    if cwd is None:
        cwd = os.getwd()
    q = ""
    for ll in levels:
        q = os.path.join(q, get_level_name(ll, cwd))
        if ll == target_level:
            break
    return q

def normpath(cwd):
    """
    Normalize the path in `cwd` by referring it to the lowest level
    in the current hierarchy.
    """
    this_level = level(cwd)
    this_idx = levels.index(this_level)
    parts = cwd.split(os.path.sep)
    return os.path.join(*parts[-this_idx:])
