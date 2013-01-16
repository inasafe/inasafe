# ~/fabfile.py

import os
from fabric.api import *
from fabric.contrib.files import contains, exists, append, sed
env.hosts = ['localhost']

def remote_info():
    env.user  = run('whoami')
    run('uname -a')

def local_info():
    local.user  = run('whoami')
    local('uname -a')

def initialise_repo():
    """Initialise a local repo for nightly builds"""

    fab_path = os.path.dirname(__file__)
    local_path = '%s/scripts/nightly-build-repo' % fab_path
    dest_path = '/home/web/inasafe-nightly'
    local('mkdir -p %s' % dest_path)
    freshen_repo()

    local('cp %(local_path)s/inasafe-nightly.conf.templ '
        '%(local_path)s/inasafe-nightly.conf' % {'local_path': local_path})

    sed('%s/inasafe-nightly.conf' % local_path, 'inasafe-nightly.linfiniti.com',
        'inasafe-nightly.localhost')

    with cd('/etc/apache2/sites-available/'):
        if exists('inasafe-nightly.conf'):
            sudo('a2dissite inasafe-nightly.conf')
            fastprint('Removing old apache2 conf', False)
            sudo('rm inasafe-nightly.conf')

        sudo('ln -s %s/inasafe-nightly.conf .' % local_path)

    # Add a hosts entry for local testing
    hosts = '/etc/hosts'
    if not contains(hosts, 'inasafe-nightly'):
        append(hosts, '127.0.0.1 inasafe-nightly.localhost', use_sudo=True)

    sudo('a2ensite inasafe-nightly.conf')
    sudo('service apache2 reload')

def freshen_repo():
    """Copy all content files from git repo to web repo.

    .. note:: You should have run initialise_repo at least once first.

    """
    fab_path = os.path.dirname(__file__)
    local_path = '%s/scripts/nightly-build-repo' % fab_path
    dest_path = '/home/web/inasafe-nightly'
    if exists(dest_path):
        put('%s/plugin*' % local_path, dest_path)
        put('%s/icon*' % local_path, dest_path)
    else:
        fastprint('Repo does not exist - run initialise_repo first')



