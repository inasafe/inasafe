# ~/fabfile.py
# A Fabric file for carrying out various administrative tasks with InaSAFE.
# Tim Sutton, Jan 2013

import os
from datetime import datetime
from fabric.api import *
from fabric.contrib.files import contains, exists, append, sed
env.hosts = ['localhost']
site_name = 'inasafe-nightly.localhost'
dest_path = '/home/web/inasafe-nightly'


def remote_info():
    env.user = run('whoami')
    run('uname -a')


def local_info():
    local.user = run('whoami')
    local('uname -a')


def initialise_repo():
    """Initialise a local repo for nightly builds"""

    fab_path = os.path.dirname(__file__)
    local_path = '%s/scripts/nightly-build-repo' % fab_path
    local('mkdir -p %s' % dest_path)
    freshen_repo()

    local('cp %(local_path)s/inasafe-nightly.conf.templ '
        '%(local_path)s/inasafe-nightly.conf' % {'local_path': local_path})

    sed('%s/inasafe-nightly.conf' % local_path,
        'inasafe-nightly.linfiniti.com',
        site_name)

    with cd('/etc/apache2/sites-available/'):
        if exists('inasafe-nightly.conf'):
            sudo('a2dissite inasafe-nightly.conf')
            fastprint('Removing old apache2 conf', False)
            sudo('rm inasafe-nightly.conf')

        sudo('ln -s %s/inasafe-nightly.conf .' % local_path)

    # Add a hosts entry for local testing
    hosts = '/etc/hosts'
    if not contains(hosts, 'inasafe-nightly'):
        append(hosts, '127.0.0.1 %s' % site_name, use_sudo=True)

    sudo('a2ensite inasafe-nightly.conf')
    sudo('service apache2 reload')


def freshen_repo():
    """Copy all content files from git repo to web repo.

    .. note:: You should have run initialise_repo at least once first.

    """
    fab_path = os.path.dirname(__file__)
    local_path = '%s/scripts/nightly-build-repo' % fab_path

    if exists(dest_path):
        put('%s/plugin*' % local_path, dest_path)
        put('%s/icon*' % local_path, dest_path)
    else:
        fastprint('Repo does not exist - run initialise_repo first')


def build_nightly():
    """Create a nightly package and publish it in our repo."""
    dir_name = os.path.dirname(__file__)
    dir_name = os.path.split(dir_name)[-1]
    fastprint('Dir is: %s' % dir_name)

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
    package_name = '%s.%s.zip' % (dir_name, plugin_version)
    source = '/tmp/%s' % package_name
    fastprint('Source: %s' % source)
    put(source, dest_path)

    plugins_xml = os.path.join(dest_path, 'plugins.xml')
    sed(plugins_xml, '\[VERSION\]', plugin_version)
    sed(plugins_xml, '\[FILE_NAME\]', package_name)
    sed(plugins_xml, '\[URL\]', 'http://%s/%s' % (site_name, package_name))
    sed(plugins_xml, '\[DATE\]', str(datetime.now()))
