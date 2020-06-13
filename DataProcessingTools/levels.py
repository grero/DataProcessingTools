import os
import glob

levels = ['subjects', 'subject', 'day', 'session', 'array', 'channel','cell']
level_patterns_s = ["*", "*", "[0-9]*", "session[0-9]*", "array[0-9]*", "channel[0-9]*", "cell[0-9]*"]


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
    for i in range(0, this_idx - target_idx+1):
        pl.append("..")
    print(pl)
    return os.path.join(*pl)
