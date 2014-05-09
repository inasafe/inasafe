# coding=utf-8
"""A Fabric file for carrying out various administrative tasks with InaSAFE.

Usage for localhost commands::

    fab -H localhost [command]
    fab -H 188.40.123.80:8697 show_environment

To run on a vagrant vhost do::

    fab vagrant [command]

e.g. ::

    fab vagrant show_environment

.. note:: Vagrant tasks will only run if they @task decorator is used on
    the function. See show_environment function below.

Tim Sutton, Jan 2013
"""

import os
from datetime import datetime

from fabric.api import fastprint, env, run, hide, sudo, cd, task, get, hosts
from fabric.colors import blue, red, green
from fabric.contrib.files import contains, exists, append, sed

import fabtools
from fabtools import require

# Don't remove even though its unused
# noinspection PyUnresolvedReferences
from fabtools.vagrant import vagrant
# noinspection PyUnresolvedReferences
from fabgis.inasafe import setup_inasafe
from fabgis.git import update_git_checkout
from fabgis.common import show_environment, setup_env


def get_vars():
    """Helper method to get standard deployment vars.

    :returns: A tuple containing the following:
        * base_path: Workspace dir e.g. ``/home/foo/python``
        * code_path: Project dir e.g. ``/home/foo/python/inasafe``
        * git_url: Url for git checkout - use http for read only checkout
        * repo_alias: Name of checkout folder e.g. ``inasafe-dev``
        * site_name: Name for the web site e.g. ``experimental.inasafe.org``

    :rtype: tuple
    """
    setup_env()
    fastprint(green('Getting project variables\n'))
    site_name = 'experimental.inasafe.org'
    base_path = '/home/%s/dev/python' % env.user
    git_url = 'git://github.com/AIFDR/inasafe.git'
    repo_alias = 'inasafe-test'
    code_path = os.path.abspath(os.path.join(base_path, repo_alias))
    return base_path, code_path, git_url, repo_alias, site_name


###############################################################################
# Next section contains helper methods tasks
###############################################################################

def initialise_qgis_plugin_repo(web_directory='/home/web/inasafe-test'):
    """Initialise a QGIS plugin repo where we host test builds.

    :param web_directory: Directory for experimental plugin that will be
        published via apache.
    :type web_directory: str

    """
    base_path, code_path, git_url, repo_alias, site_name = get_vars()
    sudo('apt-get update')
    fabtools.require.deb.package('libapache2-mod-wsgi')
    local_path = '%s/scripts/test-build-repo' % code_path

    if not exists(base_path):
        sudo('mkdir -p %s' % base_path)
        sudo('chown %s.%s %s' % (env.user, env.user, base_path))

    run('cp %s/plugin* %s' % (local_path, web_directory))
    run('cp %s/icon* %s' % (code_path, web_directory))
    run('cp %(local_path)s/inasafe-test.conf.templ '
        '%(local_path)s/inasafe-test.conf' % {'local_path': local_path})

    sed('%s/inasafe-test.conf' % local_path,
        'inasafe-test.linfiniti.com', site_name)

    with cd('/etc/apache2/sites-available/'):
        if exists('inasafe-test.conf'):
            sudo('a2dissite inasafe-test.conf')
            fastprint('Removing old apache2 conf')
            sudo('rm inasafe-test.conf')

        sudo('ln -s %s/inasafe-test.conf .' % local_path)

    # Add a hosts entry for local testing - only really useful for localhost
    repo_hosts = '/etc/hosts'
    if not contains(repo_hosts, 'inasafe-test'):
        append(repo_hosts, '127.0.0.1 %s' % site_name, use_sudo=True)

    sudo('a2ensite inasafe-test.conf')
    sudo('service apache2 reload')

###############################################################################
# Next section contains actual tasks
###############################################################################


@hosts('linfiniti3')
@task
def build_test_package(
        branch='develop',
        web_directory='/home/web/inasafe-test'):
    """Create a test package and publish it in our repo.

    :param branch: The name of the branch to build from. Defaults to 'develop'.
    :type branch: str

    :param web_directory: Directory for experimental plugin that will be
        published via apache.
    :type web_directory: str

    To run e.g.::

        fab -H <host:port> build_test_package

        or to package up a specific branch (in this case minimum_needs)

        fab -H <host:port> build_test_package:minimum_needs

    .. note:: Using the branch option will not work for branches older than 1.1
    """
    base_path, code_path, git_url, repo_alias, site_name = get_vars()
    show_environment()
    update_git_checkout(base_path, git_url, repo_alias, branch)
    initialise_qgis_plugin_repo()
    fabtools.require.deb.packages(['zip', 'make', 'gettext'])

    with cd(code_path):
        # Get git version and write it to a text file in case we need to cross
        # reference it for a user ticket.
        sha = run('git rev-parse HEAD > git_revision.txt')
        fastprint('Git revision: %s' % sha)

        get('metadata.txt', '/tmp/metadata.txt')
        metadata_file = file('/tmp/metadata.txt')
        metadata_text = metadata_file.readlines()
        metadata_file.close()
        for line in metadata_text:
            line = line.rstrip()
            if 'version=' in line:
                plugin_version = line.replace('version=', '')
            if 'status=' in line:
                line.replace('status=', '')

        # noinspection PyUnboundLocalVariable
        run('scripts/release.sh %s' % plugin_version)
        package_name = '%s.%s.zip' % ('inasafe', plugin_version)
        source = '/tmp/%s' % package_name
        fastprint(blue('Source: %s\n' % source))
        run('cp %s %s' % (source, web_directory))

        source = os.path.join('scripts', 'test-build-repo', 'plugins.xml')
        plugins_xml = os.path.join(web_directory, 'plugins.xml')
        fastprint(blue('Source: %s\n' % source))
        run('cp %s %s' % (source, plugins_xml))

        sed(plugins_xml, '\[VERSION\]', plugin_version)
        sed(plugins_xml, '\[FILE_NAME\]', package_name)
        sed(plugins_xml, '\[URL\]', 'http://%s/%s' % (
            site_name, package_name))
        sed(plugins_xml, '\[DATE\]', str(datetime.now()))

        fastprint('Add http://%s/plugins.xml to QGIS plugin manager to use.'
                  % site_name)
