import datetime
import os
import subprocess


def get_version(version=None):
    """Returns a PEP 386-compliant version number from VERSION."""

    if version is None:
        # Get location of application wide version info
        rootdir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               '..', '..'))
        fid = open(os.path.join(rootdir, 'metadata.txt'))
        for line in fid.readlines():
            if line.startswith('version'):
                verstring = line.strip().split('=')[1]
                verlist = verstring.split('.')

            if line.startswith('status'):
                status = line.strip().split('=')[1]
        fid.close()
        version = tuple(verlist + [status] + [0])

    if len(version) != 5:
        msg = ('Version must be a tuple of length 5. '
               'I got %s' % str(version))
        raise RuntimeError(msg)

    if version[3] not in ('alpha', 'beta', 'rc', 'final'):
        msg = ('Version tuple not as expected. '
               'I got %s' % str(version))
        raise RuntimeError(msg)

    # Now build the two parts of the version number:
    # main = X.Y[.Z]
    # sub = .devN - for pre-alpha releases
    #     | {a|b|c}N - for alpha, beta and rc releases
    parts = 2 if version[2] == 0 else 3
    main = '.'.join(str(x) for x in version[:parts])

    sub = ''
    # This crashes on windows
    if version[3] == 'alpha' and version[4] == 0:
        git_changeset = get_git_changeset()
        if git_changeset:
            sub = '.dev%s' % git_changeset

    elif version[3] != 'final':
        mapping = {'alpha': 'a', 'beta': 'b', 'rc': 'c'}
        sub = mapping[version[3]] + str(version[4])

    return main + sub


def get_git_changeset():
    """Returns a numeric identifier of the latest git changeset.

    The result is the UTC timestamp of the changeset in YYYYMMDDHHMMSS format.
    This value isn't guaranteed to be unique, but collisions are very unlikely,
    so it's sufficient for generating the development version numbers.
    """
    repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    git_show = subprocess.Popen('git show --pretty=format:%ct --quiet HEAD',
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            shell=True, cwd=repo_dir, universal_newlines=True)
    timestamp = git_show.communicate()[0].partition('\n')[0]
    try:
        timestamp = datetime.datetime.utcfromtimestamp(int(timestamp))
    except ValueError:
        return None
    return timestamp.strftime('%Y%m%d%H%M%S')
