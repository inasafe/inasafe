Set up of Windows 'slave' builds for Jenkins
============================================

Outline of procedure:
---------------------

Set up a virtual machine. In our testing regieme we will be using:

* Windows 8 64bit
* Windows 8 32bit
* Windows 7 64bit
* Windows 7 32bit

We have purchased licenses of these OS's specifically for deployment in
our VirtualBox virtual machines. The setup and installation of windows and
VirtualBox is not described here except as pertains to testing. We will be
installing the following components on each windows slave:

* **Microsoft .net 3.5 (versions 4+ are not supported).** Under windows 8 you
  need to do this as an explicit install as the OS ships with .net 4.5. .net is
  needed to run the Jenkins service.
* **Python 2.7.** Although QGIS ships with a python interpreter, we need
  to install our own copy to support running unit tests and so on.
* **QGIS (1.8 at time of writing).** The unit tests depend on QGIS being present
  to run.
* **GitHub for Windows.** This is the convenient windows GIT client provided
  by GitHub - we will use it to clone and update our repositories.

With the base software installed, we will clone two GitHub repositories to
the VM:

* **InaSAFE.** The application that we will be testing.
* **inasafe_data.** Test data required for unit testing the InaSAFE library.

Then we will configure the system to be able to run the unit tests, first
independently of Jenkins, and then as a Jenkins job.

Lastly, we will configure the VM Jenkins instance to be a slave for our Jenkins
master and fire off the InaSAFE test suite in the VM whenever a commit is made
to the InaSAFE master branch.

We will try to keep things as simple as possible. The VM instances should not
be used for any other purpose in order to keep them small, fast and to avoid
configuration issues caused by conflicting libraries.

VM Configuration:
-----------------

We used the following configuration options when creating our virtual machines:

* 4 GB Ram (thus your host OS needs 8GB or more)
* 25 GB Virtual Hard Disk
* Installation of guest extensions.

All virtual machines were created using the free VirtualBox software.

Note that you may need to enable virtualisation in your PC bios too.

All Virtual Machines were created with a *local* user account with

Username: inasafe
Password: XXXXXX (redacted)

We did not enable the new 'cloud login' options of Windows 8.

After the windows installation, we turned off all extraneous services to
maximise performance and increase test times.

Software Installation
----------------------

The following were the standard software installed on each Windows VM:

QGIS Install
............

* Install QGIS standalone from http://download.qgis.org
* Create the .qgis\python\plugins dir

GitHub for Windows Install
..........................

* Install from http://windows.github.com
* Do not log in with your account details (for security)
* In options, set your default storage directory to
  :file:`C:\Users\inasafe\.qgis\python\plugins`

Copy over the repositories from the host system (quickest) or check them out
from github anonymously. If you take the former route, after copying them in
to the plugins directory use the GitHub Windows app's options dialog to find
them by clicking the 'scan for repositories' button.


Python Install
..............


* Download and install Python **32Bit** (even if you are running a 64 bit
  windows!!!) to match the version of python shipped with QGIS (python 2.7 in
  the case of QGIS 1.8).
* Follow the process described in :ref:`windows_shell_launcher-label` so that
  you can use the QGIS libraries from a python shell. Note that you probably
  need to change the second last line of that script to :samp:`cd "%HOMEPATH%\
  .qgis\python\plugins\inasafe"` (removing the '-dev') at the end.
* Follow the processed described in :ref:`windows-nose-setup` so that you have
  a working pip, nose etc.

Now run the tests and ensure that they can be run from the command line
*before* attempting to run them via Jenkins::

    C:\Users\inasafe\.qgis\python\plugins\inasafe>runtests.bat

.net 3.5 Install
................

To install Jenkins, you first need to ensure you have .net 3.5 on your system.
Windows 8 ships with .net 4+ so you need to manually install the older version
too. First visit http://www.microsoft.com/en-us/download/details.aspx?id=21
and either choose the .NET Framework Full Package (around 200mb, the option
I took) or get the online installer. Note that the full package link is near
the bottom of the page.

Run the installer and accept all the defaults to install the .net 3.5
framework.

Jenkins Install
...............

Simply go to http://jenkins-ci.org/ and download the windows native package
 and then install it, taking all the defaults.

Once Jenkins is set up, open your browser at http://localhost:8080 to access
the Jenkins page.


Jenkins Configuration
---------------------

Plugins
.......

The first thing you need to do is install some jenkins plugins. To do this
do :menuselection:`Manage Jenkins --> Manage Plugins --> Available tab`.

Now install at least these plugins:

* Jenkins GIT plugin
* GitHub API plugin
* GitHub plugin

In addition these plugins should be available by default:

* Jenkins mailer plugin
* External Monitor Job Type Plugin
* pam-auth

For simplicity, I also disabled the following plugins:

* LDAP Plugin
* ant
* javadoc
* Jenkins CVS Plug-in
* Maven Integration plugin
* Jenkins SSH Slaves plugins
* Jenkins Subversion plugin
* Jenkins Translation Assistance plugin

System configuration
....................
7
We need to provide the path to git so that Jenkins can automatically make
checkouts of each version.

:menuselection:`Jenkins --> Manage Jenkins --> Configuration --> Git
Installations --> Path to Git executable` needs to be set. On my system I used
the following path::

    C:\Users\inasafe\AppData\Local\GitHub\PortableGit_93e8418133eb85e81a81e5e19c272776524496c6\bin\git.exe

The GitHub application's git installer is a portable app and the path for you
is going to look a little different - just lookin in your AppData dir and you
should find it.

.. note:: The Jenkins system user will need to have read permissions on the
    above directory.

Next populate the options in:

* :menuselection:`Jenkins --> Manage Jenkins --> Configuration --> Git Plugins`:

* :menuselection:`Global Config user.name Value` : :kbd:`<your name>`
* :menuselection:`Global Config user.email Value` : :kbd:`<your@email.com>
* :menuselection:`Create new accounts base on author/committer's email` : no

Now click the :guiselection:`Save Button` to save your global configuration
changes.

Job Configuration
.................

Next we create our build job with the following options:

* :menuselection:`Project name` : :kbd:`inasafe-win8-64` (adjust the name as
  appropriate)
* :menuselection:`Build a free-style software project` : select

On the job configuration page use the following options:

* :menuselection:`Description` : :kbd:`Windows 8 64 bit build of InaSAFE`
* :menuselection:`GitHub project` : :kbd:`http://github.com/AIFDR/inasafe/`
* :menuselection:`Source Code Management` section
* :menuselection:`Git` : Check
* :menuselection:`Repository URL` : :kbd:`git://github.com/AIFDR/inasafe.git`
* :menuselection:`Branches to build` : :kbd:`version-1_1`
* :menuselection:`Repository browser` : :kbd:`githubweb`
* :menuselection:`Url` : :kbd:`http://github.com/AIFDR/inasafe/`

* :menuselection:`Build triggers` section
* :menuselection:`Poll SCM` : check and set to :kbd:`* * * * *` for
  minutely checks.

Save your changes at this point and make a commit, you should see the job
produce output something like this the next time a commit takes place::

    Started by timer
    Building in workspace C:\Jenkins\jobs\inasafe-win8-64\workspace
    Checkout:workspace / C:\Jenkins\jobs\inasafe-win8-64\workspace - hudson.remoting.LocalChannel@1fd5730
    Using strategy: Default
    Last Built Revision: Revision 5403e3ba45129b42edaa2bc0ebd12e8c9ead868e (origin/version-1_1)
    Fetching changes from 1 remote Git repository
    Fetching upstream changes from git://github.com/AIFDR/inasafe.git
    Commencing build of Revision 5403e3ba45129b42edaa2bc0ebd12e8c9ead868e (origin/version-1_1)
    Checking out Revision 5403e3ba45129b42edaa2bc0ebd12e8c9ead868e (origin/version-1_1)
    Finished: SUCCESS

That validates that at least your git checkout is working as expected.


