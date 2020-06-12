import os
levels = ['day', 'session', 'array', 'channel']


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
