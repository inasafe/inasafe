Frequently Asked Questions
==========================



I found a bug, how should I report it?
--------------------------------------

We manage the project issues using a GitHub issue tracker. The
`InaSAFE <https://github.com/AIFDR/inasafe/issues?direction=desc&sort=created&state=open>`_
issue tracker is open to everyone, though you will first need to register a
(free) account on GitHub to use it. You can find the GitHub self-registration
page `here <https://github.com/signup/free>`_.

Why can't I find the plugin in the QGIS repositories?
-----------------------------------------------------

We do plan to publish the plugin at
`plugins.qgis.org <http://plugins.qgis.org/>`_ so that it can be effortlessly
installed from within QGIS, we are just no ready to do that yet. In the mean
time please use the manual installation procedure to install InaSAFE in QGIS.

Do I need to pay to use |project_name|?
---------------------------------------

No, the software is completely Free and Open Source.

What license is |project_name| published under?
-----------------------------------------------

|project_name| is published under the GPL version 2 license, the full text of
which is available at 
`www.gnu.org/licenses/gpl-2.0.txt <http://www.gnu.org/licenses/gpl-2.0.txt>`_.


Under the terms of the license of you may freely copy, share and modify the
software, as long as you make it available under the same license.

How is the project funded?
--------------------------

The project is being developed 'for the good of humanity' and has been 
jointly developed by `BNPB <http://www.bnpb.go.id/>`_, 
`AusAid <http://www.ausaid.gov.au/>`_ & 
`the World Bank <http://www.worldbank.org/>`_.

Could we request a new feature?
-------------------------------

If you have a feature request, please use the 
`issue tracker <https://github.com/AIFDR/inasafe/issues?direction=desc&sort=created&state=open>`_ 
to let us know about it, using the same procedure as for bug reporting.

How did you embed the git version SHA1 into each .py file?
----------------------------------------------------------

The format was derived using the `git log format tag <http://schacon.github.com/git/git-log.html>`_.
It is stored in the source of each python as::
   
   __revision__ = '$Format:%H$'

'%H' being the format tag for the SHA1. The __revision__ is **not** updated
with each commit. Rather is is registered with git for replacement when using
git-archive by doing this::
   
   echo "*.py export-subst" > .gitattributes
   git add .gitattributes

The above only needs to be done once and then all python files with format
substitutions will be replaced when running git-archive. The actual substition
takes place at the time that a git archive is generated (git archive creates a
copy of the repo with all repository metadata stripped out). For example::
  
  git archive version-0_3 | tar -x -C /tmp/inasafe-0.3.0

You can verify SHA1 replacement has been made by doing::
   
   cat /tmp/inasafe/gui/is_plugin.py | grep revision
   __revision__ = 'a515345e43b25d065e1ae0d73687c13531ea4c9c'

The deployment of version tagged files is automated by using the 
:file:`scripts\release.sh` script.
   
