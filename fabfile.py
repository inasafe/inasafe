# ~/fabfile.py
# A Fabric file for carrying out various administrative tasks with InaSAFE.
# Tim Sutton, Jan 2013

import os
from datetime import datetime
from fabric.api import *
from fabric.contrib.files import contains, exists, append, sed

# Usage fab localhost [command]
#    or fab remote [command]
#  e.g. fab localhost initialise_repo

# Global fabric settings

def captured_local(command):
    """A wrapper around local that always returns output."""
    return local(command, capture=True)

def localhost():
    """Set up things so that commands run locally."""
    env.run = captured_local
    env.hosts = ['localhost']
    all()

def remote():
    """Set up things so that commands run remotely.
    To run remotely do e.g.::

        fab -H 188.40.123.80:8697 remote show_environment

    """
    env.run = run
    all()

def all():
    """Things to do regardless of whether command is local or remote."""
    site_names = {
        'waterfall': 'inasafe-nightly.localhost',
        'maps.linfiniti.com': 'inasafe-nightly.linfiniti.com'}
    with hide('output'):
        env.user = env.run('whoami')
        env.hostname = env.run('hostname')
        if env.hostname not in site_names:
            print 'Error: %s not in: \n%s' % (env.hostname, site_names)
            exit
        else:
            env.site_name = site_names[env.hostname]
            env.dest_path = '/home/web/inasafe-nightly'
            show_environment()

###############################################################################
# Next section contains actual tasks
###############################################################################

def initialise_repo():
    """Initialise a local repo for nightly builds"""

    fab_path = os.path.dirname(__file__)
    local_path = '%s/scripts/nightly-build-repo' % fab_path
    local('mkdir -p %s' % env.dest_path)
    freshen_repo()

    local('cp %(local_path)s/inasafe-nightly.conf.templ '
        '%(local_path)s/inasafe-nightly.conf' % {'local_path': local_path})

    sed('%s/inasafe-nightly.conf' % local_path,
        'inasafe-nightly.linfiniti.com',
        env.site_name)

    with cd('/etc/apache2/sites-available/'):
        if exists('inasafe-nightly.conf'):
            sudo('a2dissite inasafe-nightly.conf')
            fastprint('Removing old apache2 conf', False)
            sudo('rm inasafe-nightly.conf')

        sudo('ln -s %s/inasafe-nightly.conf .' % local_path)

    # Add a hosts entry for local testing
    hosts = '/etc/hosts'
    if not contains(hosts, 'inasafe-nightly'):
        append(hosts, '127.0.0.1 %s' % env.site_name, use_sudo=True)

    sudo('a2ensite inasafe-nightly.conf')
    sudo('service apache2 reload')


def freshen_git():
    """Make sure there is a read only git checkout."""

    git_url = 'git://github.com/AIFDR/inasafe.git'
    


def freshen_repo():
    """Copy all content files from git repo to web repo.

    .. note:: You should have run initialise_repo at least once first.

    """
    fab_path = os.path.dirname(__file__)
    local_path = '%s/scripts/nightly-build-repo' % fab_path

    if exists(env.dest_path):
        put('%s/plugin*' % local_path, env.dest_path)
        put('%s/icon*' % local_path, env.dest_path)
    else:
        fastprint('Repo does not exist - run initialise_repo first')


def build_nightly():
    """Create a nightly package and publish it in our repo."""
    dir_name = os.path.dirname(__file__)
    dir_name = os.path.split(dir_name)[-1]
    fastprint('Dir is: %s' % dir_name)
    # Get git version and write it to a text file in case we need to cross
    # references it for a user ticket.
    sha = local('git rev-parse HEAD', capture=True)
    fastprint('Git revision: %s' % sha)
    sha_path = 'git_revision.txt'
    sha_file = file(sha_path, 'wt')
    sha_file.write(sha)
    sha_file.close()

    freshen_repo()

    metadata_file = file('metadata.txt', 'rt')
    metadata_text = metadata_file.readlines()
    metadata_file.close()
    for line in metadata_text:
        line = line.rstrip()
        if 'version=' in line:
            plugin_version = line.replace('version=', '')
        if 'status=' in line:
            status = line.replace('status=', '')

    local('scripts/release.sh %s' % plugin_version)
    package_name = '%s.%s.zip' % ('inasafe', plugin_version)
    source = '/tmp/%s' % package_name
    fastprint('Source: %s' % source)
    put(source, env.dest_path)

    plugins_xml = os.path.join(env.dest_path, 'plugins.xml')
    sed(plugins_xml, '\[VERSION\]', plugin_version)
    sed(plugins_xml, '\[FILE_NAME\]', package_name)
    sed(plugins_xml, '\[URL\]', 'http://%s/%s' % (env.site_name, package_name))
    sed(plugins_xml, '\[DATE\]', str(datetime.now()))

    os.remove(sha_path)

    fastprint('Add http://%s/plugins.xml to QGIS plugin manager to use this.'
        % sha)

def show_environment():
    """For diagnostics - show any pertinent info about server."""
    fastprint('\n-------------------------------------------------\n')
    fastprint('User: %s\n' % env.user)
    fastprint('Host: %s\n' % env.hostname)
    fastprint('Site Name: %s\n' % env.site_name)
    fastprint('Dest Path: %s\n' % env.dest_path)
    fastprint('-------------------------------------------------\n')
