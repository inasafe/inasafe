# -*- coding: utf-8 -*-
"""
Useful network functions
begin : 2011-03-01
copyright : (C) 2011 by Luiz Motta
author : Luiz P. Motta
email : motta _dot_ luiz _at_ gmail.com


.. note:: This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2 of the License, or
   (at your option) any later version.

"""
from PyQt4.QtCore import QSettings, QT_VERSION
from PyQt4.QtNetwork import QNetworkProxy


def get_proxy():
    """Adaption by source of Plugin Installer - Version 1.0.10"""
    settings = QSettings()
    settings.beginGroup('proxy')
    enabled = settings.value('/proxyEnabled', False, type=bool)
    if not enabled:
        return None

    proxy = QNetworkProxy()
    try:
        proxy_type = settings.value('/proxyType', 0, type=int)
    except TypeError:
        # Catch for this:
        # TypeError: unable to convert a QVariant of type 10 to a
        # QMetaType of type 2
        # TODO: can we do anything to handle this more gracefully? TS
        settings.setValue('/proxyType', 0)
        return proxy
    if proxy_type in ['1', 'Socks5Proxy']:
        proxy.setType(QNetworkProxy.Socks5Proxy)
    elif proxy_type in ['2', 'NoProxy']:
        proxy.setType(QNetworkProxy.NoProxy)
    elif proxy_type in ['3', 'HttpProxy']:
        proxy.setType(QNetworkProxy.HttpProxy)
    elif proxy_type in ['4', 'HttpCachingProxy'] and QT_VERSION >= 0X040400:
        proxy.setType(QNetworkProxy.HttpCachingProxy)
    elif proxy_type in ['5', 'FtpCachingProxy'] and QT_VERSION >= 0X040400:
        proxy.setType(QNetworkProxy.FtpCachingProxy)
    else:
        proxy.setType(QNetworkProxy.DefaultProxy)
    proxy.setHostName(settings.value('/proxyHost'))
    proxy.setPort(settings.value('/proxyPort', type=int))
    user = settings.value('/proxyUser', type=str)
    password = settings.value('/proxyPassword', type=str)
    if user is not None:
        proxy.setUser(user)
    if password is not None and user is not None:
        proxy.setPassword(password)
    settings.endGroup()
    return proxy
