IRC Notes for InaSAFE
=====================

The IRC channel is #inasafe on freenode.

The channel is logged, you can read the logs at http://irclogs.geoapt.com/inasafe/.

Tim (timlinux) has ops and has registered the channel::

   /query chanserv
   register #inasafe

To obtain ops after logging off do::

   /query chanserv
   op #inasafe timlinux

To give others op status in the channel do::

  /op <user>

There is a github hook enabled 'IRC"
https://github.com/AIFDR/inasafe/admin/hooks with the following settings:

* **server** : irc.freenode.net
* **port** : 6667
* **room** : inasafe
* **nick** : gh-inasafe
* **branch regexes** : (leave blank)
* **password** : (leave blank)
* **ssl** : no
* **message without join** : yes
* **no colors** : no
* **Long URL** : yes
* **Notice** : yes
* **Active** : yes

Also you need to do a mode change on the chanserv channel to enable outsider messages::

   /query chanserv
   set #inasafe mlock -n

