# ~/fabfile.py
# A Fabric file for carrying out various administrative tasks with InaSAFE.
# Tim Sutton, Jan 2013

import os
from datetime import datetime
from fabric.api import *
from fabric.contrib.files import contains, exists, append, sed

# Usage fab localhost [command]
#    or fab remote [command]
#  e.g. fab localhost update_qgis_plugin_repo

# Global fabric settings


def captured_local(command):
    """A wrapper around local that always returns output."""
    return local(command, capture=True)


def localhost():
    """Set up things so that commands run locally."""
    env.run = captured_local
    env.hosts = ['localhost']
    _all()


def remote():
    """Set up things so that commands run remotely.
    To run remotely do e.g.::

        fab -H 188.40.123.80:8697 remote show_environment

    """
    env.run = run
    _all()


def _all():
    """Things to do regardless of whether command is local or remote."""

    # Key is hostname as it resolves by running hostname directly on the server
    # value is desired web site url to publish the repo as.
    doc_site_names = {
        'waterfall': 'inasafe-docs.localhost',
        'spur': 'inasafe-docs.localhost',
        'maps.linfiniti.com': 'inasafe-docs.linfiniti.com',
        'linfiniti': 'inasafe-docs.linfiniti.com',
        'shiva': 'docs.inasafe.org'}
    repo_site_names = {
        'waterfall': 'inasafe-test.localhost',
        'spur': 'inasafe-test.localhost',
        'maps.linfiniti.com': 'inasafe-test.linfiniti.com',
        'linfiniti': 'inasafe-crisis.linfiniti.com',
        'shiva': 'experimental.inasafe.org'}

    with hide('output'):
        env.user = env.run('whoami')
        env.hostname = env.run('hostname')
        if env.hostname not in repo_site_names:
            print 'Error: %s not in: \n%s' % (env.hostname, repo_site_names)
            exit
        elif env.hostname not in doc_site_names:
            print 'Error: %s not in: \n%s' % (env.hostname, repo_site_names)
            exit
        else:
            env.repo_site_name = repo_site_names[env.hostname]
            env.doc_site_name = doc_site_names[env.hostname]
            env.plugin_repo_path = '/home/web/inasafe-test'
            env.inasafe_docs_path = '/home/web/inasafe-docs'
            env.home = os.path.join('/home/', env.user)
            env.repo_path = os.path.join(env.home,
                                         'dev',
                                         'python')
            env.git_url = 'git://github.com/AIFDR/inasafe.git'
            env.repo_alias = 'inasafe-test'
            show_environment()

###############################################################################
# Next section contains helper methods tasks
###############################################################################


def update_qgis_plugin_repo():
    """Initialise a QGIS plugin repo where we host test builds."""
    code_path = os.path.join(env.repo_path, env.repo_alias)
    local_path = '%s/scripts/test-build-repo' % code_path

    if not exists(env.plugin_repo_path):
        sudo('mkdir -p %s' % env.plugin_repo_path)
        sudo('chown %s.%s %s' % (env.user, env.user, env.plugin_repo_path))

    env.run('cp %s/plugin* %s' % (local_path, env.plugin_repo_path))
    env.run('cp %s/icon* %s' % (code_path, env.plugin_repo_path))
    env.run('cp %(local_path)s/inasafe-test.conf.templ '
            '%(local_path)s/inasafe-test.conf' % {'local_path': local_path})

    sed('%s/inasafe-test.conf' % local_path,
        'inasafe-test.linfiniti.com',
        env.repo_site_name)

    with cd('/etc/apache2/sites-available/'):
        if exists('inasafe-test.conf'):
            sudo('a2dissite inasafe-test.conf')
            fastprint('Removing old apache2 conf', False)
            sudo('rm inasafe-test.conf')

        sudo('ln -s %s/inasafe-test.conf .' % local_path)

    # Add a hosts entry for local testing - only really useful for localhost
    hosts = '/etc/hosts'
    if not contains(hosts, 'inasafe-test'):
        append(hosts, '127.0.0.1 %s' % env.repo_site_name, use_sudo=True)

    sudo('a2ensite inasafe-test.conf')
    sudo('service apache2 reload')


def update_qgis_docs_site():
    """Initialise an InaSAFE docs sote where we host test pdf."""
    code_path = os.path.join(env.repo_path, env.repo_alias)
    local_path = '%s/scripts/test-build-repo' % code_path

    if not exists(env.inasafe_docs_path):
        sudo('mkdir -p %s' % env.inasafe_docs_path)
        sudo('chown %s.%s %s' % (env.user, env.user, env.inasafe_docs_path))

    env.run('cp %s/plugin* %s' % (local_path, env.plugin_repo_path))
    env.run('cp %s/icon* %s' % (code_path, env.plugin_repo_path))
    env.run('cp %(local_path)s/inasafe-test.conf.templ '
            '%(local_path)s/inasafe-test.conf' % {'local_path': local_path})

    sed('%s/inasafe-test.conf' % local_path,
        'inasafe-test.linfiniti.com',
        env.repo_site_name)

    with cd('/etc/apache2/sites-available/'):
        if exists('inasafe-docs.conf'):
            sudo('a2dissite inasafe-docs.conf')
            fastprint('Removing old apache2 conf', False)
            sudo('rm inasafe-docs.conf')

        sudo('ln -s %s/inasafe-docs.conf .' % local_path)

    # Add a hosts entry for local testing - only really useful for localhost
    hosts = '/etc/hosts'
    if not contains(hosts, 'inasafe-docs'):
        append(hosts, '127.0.0.1 %s' % env.repo_site_name, use_sudo=True)

    sudo('a2ensite inasafe-docs.conf')
    sudo('service apache2 reload')


def update_git_checkout(branch='master'):
    """Make sure there is a read only git checkout.

    Args:
        branch: str - a string representing the name of the branch to build
            from. Defaults to 'master'

    To run e.g.::

        fab -H 188.40.123.80:8697 remote update_git_checkout

    """

    if not exists(os.path.join(env.repo_path, env.repo_alias)):
        fastprint('Repo checkout does not exist, creating.')
        env.run('mkdir -p %s' % (env.repo_path))
        with cd(env.repo_path):
            clone = env.run('git clone %s %s' % (env.git_url, env.repo_alias))
    else:
        fastprint('Repo checkout does exist, updating.')
        with cd(os.path.join(env.repo_path, env.repo_alias)):
            # Get any updates first
            clone = env.run('git fetch')
            # Get rid of any local changes
            clone = env.run('git reset --hard')
            # Get back onto master branch
            clone = env.run('git checkout master')
            # Remove any local changes in master
            clone = env.run('git reset --hard')
            # Delete all local branches
            clone = env.run('git branch | grep -v \* | xargs git branch -D')

    with cd(os.path.join(env.repo_path, env.repo_alias)):
        if branch != 'master':
            clone = env.run('git branch --track %s origin/%s' %
                            (branch, branch))
            clone = env.run('git checkout %s' % branch)
        else:
            clone = env.run('git checkout master')
        clone = env.run('git pull')


def install_latex():
    """Ensure that the target system has a usable latex installation.

    Args:
        None

    Returns:
        None

    Raises:
        None
    """
    clone = env.run('which pdflatex')
    if '' == clone:
        env.run('sudo apt-get install texlive-latex-extra python-sphinx '
                'texinfo dvi2png')

###############################################################################
# Next section contains actual tasks
###############################################################################


def build_test_package(branch='master'):
    """Create a test package and publish it in our repo.

    Args:
        branch: str - a string representing the name of the branch to build
            from. Defaults to 'master'.

    To run e.g.::

        fab -H 188.40.123.80:8697 remote build_test_package

        or to package up a specific branch (in this case minimum_needs)

        fab -H 88.198.36.154:8697 remote build_test_package:minimum_needs

    .. note:: Using the branch option will not work for branches older than 1.1
    """

    update_git_checkout(branch)
    update_qgis_plugin_repo()

    dir_name = os.path.join(env.repo_path, env.repo_alias)
    with cd(dir_name):
        # Get git version and write it to a text file in case we need to cross
        # reference it for a user ticket.
        sha = env.run('git rev-parse HEAD > git_revision.txt')
        fastprint('Git revision: %s' % sha)

        get('metadata.txt', '/tmp/metadata.txt')
        metadata_file = file('/tmp/metadata.txt', 'rt')
        metadata_text = metadata_file.readlines()
        metadata_file.close()
        for line in metadata_text:
            line = line.rstrip()
            if 'version=' in line:
                plugin_version = line.replace('version=', '')
            if 'status=' in line:
                status = line.replace('status=', '')

        env.run('scripts/release.sh %s' % plugin_version)
        package_name = '%s.%s.zip' % ('inasafe', plugin_version)
        source = '/tmp/%s' % package_name
        fastprint('Source: %s' % source)
        env.run('cp %s %s' % (source, env.plugin_repo_path))

        plugins_xml = os.path.join(env.plugin_repo_path, 'plugins.xml')
        sed(plugins_xml, '\[VERSION\]', plugin_version)
        sed(plugins_xml, '\[FILE_NAME\]', package_name)
        sed(plugins_xml, '\[URL\]', 'http://%s/%s' %
                                    (env.repo_site_name, package_name))
        sed(plugins_xml, '\[DATE\]', str(datetime.now()))

        fastprint('Add http://%s/plugins.xml to QGIS plugin manager to use.'
                  % env.repo_site_name)


def build_documentation(branch='master'):
    """Create a pdf and html doc tree and publish them online.

    Args:
        branch: str - a string representing the name of the branch to build
            from. Defaults to 'master'.

    To run e.g.::

        fab -H 188.40.123.80:8697 remote build_documentation

        or to package up a specific branch (in this case minimum_needs)

        fab -H 88.198.36.154:8697 remote build_documentation:version-1_1

    .. note:: Using the branch option will not work for branches older than 1.1
    """

    update_git_checkout(branch)
    install_latex()

    dir_name = os.path.join(env.repo_path, env.repo_alias, 'docs')
    with cd(dir_name):
        # build the tex file
        env.run('make latex')

    dir_name = os.path.join(env.repo_path, env.repo_alias,
                            'docs', 'build', 'latex')
    with cd(dir_name):
        # Now compile it to pdf
        env.run('pdflatex -interaction=nonstopmode InaSAFE.tex')
        # run 2x to ensure indices are generated?
        env.run('pdflatex -interaction=nonstopmode InaSAFE.tex')


def show_environment():
    """For diagnostics - show any pertinent info about server."""
    fastprint('\n-------------------------------------------------\n')
    fastprint('User: %s\n' % env.user)
    fastprint('Host: %s\n' % env.hostname)
    fastprint('Site Name: %s\n' % env.repo_site_name)
    fastprint('Dest Path: %s\n' % env.plugin_repo_path)
    fastprint('Home Path: %s\n' % env.home)
    fastprint('Repo Path: %s\n' % env.repo_path)
    fastprint('Git Url: %s\n' % env.git_url)
    fastprint('Repo Alias: %s\n' % env.repo_alias)
    fastprint('-------------------------------------------------\n')
