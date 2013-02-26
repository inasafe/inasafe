
Version Control
===============

We are using git for version control. You can find all the latest source code
here: https://github.com/AIFDR/inasafe

Branching guide
---------------

|project_name| follows the following simple branching model:

.. figure:: ../static/release-workflow.png
   :align:   center


*New development* takes place in *master*. Master should always be maintained
in a usable state with tests passing and the code functional as far as possible
such that we can create a new release from master at short notice.

*Releases* should take place in long lived branches named after the minor
version number (we follow the `semantic versioning scheme <http://semver.org/>`_) so for example the first
release would be version 0.1 and would be in a branch from master called *release_0-1*.

After the minor release branch is made, the *point releases (patch)* are created as tags
off that branch. For example the release flow for version 0.1.0  would be:

* branch release_0.1 from master
* apply any final polishing the the relase_0-1 branch
* when we are ready to release, tag the branch as release_0-1-0
* create packages from a checkout of the tag


After the release, development should take place in master. Additional short lived
branches can be made off master while new features are worked on, and then merged into
master when they are ready.

Optionally, development can also be carried out in independent forks of the inasafe
repository and then merged into master when they are ready via a pull request or patch.

Commits to master that constitute bug fixes to existing features should be backported to
the current release branch using the :samp:`git cherry-pick` command. Alternatively, if
a fix is made in the release branch, the changeset should be applied to master where
appropriate in order to ensure that master includes all bug fixes from the release branches.


Process for developers adding a new feature
-------------------------------------------

Create a feature branch
    * git checkout -b <featurebranch> master


Write new code and tests
    ...

Publish (if unfinished)
    * git commit -a -m "I did something wonderful"
    * git push origin <featurebranch>

To keep branch up to date:

    * git checkout <featurebranch>
    * git merge origin master
    * (possibly resolve conflict and verify test suite runs)
    * git push origin <featurebranch>


When all tests pass, either merge into master

    * git checkout master
    * git merge --no-ff <featurebranch>
      (possibly resolve conflict and verify test suite runs)
    * git push origin master


Or issue a pull request through github
    ..

To delete when branch is no longer needed (though it is preferable to do
such work in a fork of the official repo).

    * git push origin :<featurebranch>


Process for checking out the release branch and applying a fix:
---------------------------------------------------------------

Create a local `tracking branch <http://book.git-scm.com/4_tracking_branches.html>`_::

   git fetch
   git branch --track release-0_1 origin/release-0_1
   git checkout release-0_1

Now apply your fix, test and commit::

   git commit -m "Fix issue #22 - results do not display"
   git push

To backport the fix to master do (you should test after cherry picking and
before pushing though)::

   git checkout master
   git cherry-pick 0fh12
   git push

To checkout someone else's fork:
--------------------------------

Example::

   git remote add jeff git://githup.com/jj0hns0n/riab.git
   git remote update
   git checkout -b impact_map jeff/impact_map


Windows Specific Notes:
-----------------------

To Switch branches using TortioiseGIT:

* Navigate to the inasafe plugin folder
* Right click on any whitespace
* From the context menu choose TortoiseGIT->Switch/Checkout
* Tick 'Branch radio button and choose 'master' from the list
* Click ok

To update the master branch:


* Right click on the whitespace again
* TortoiseGIT->Pull from the context menu
* Tick the remote radio
* Set remote to origin
* Tick the ellipses button next to 'Remote Branch'
* Choose 'master' from the list
* Click OK

For subsequent pull requests on that branch you can just do TortoiseGIT->Pull
from the context menu and press ok
