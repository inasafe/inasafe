# -*- coding: utf-8 -*-
"""
/***************************************************************************
    Useful network functions
                             -------------------
    begin            : 2011-03-01
    copyright        : (C) 2011 by Luiz Motta
    author           : Luiz P. Motta
    email            : motta _dot_ luiz _at_ gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QVariant, QT_VERSION
from PyQt4.QtNetwork import QNetworkProxy


def get_proxy():
    """Adaption by source of Plugin Installer - Version 1.0.10"""
    settings = QSettings()
    settings.beginGroup("proxy")
    #if settings.value("/proxyEnabled").toBool():
    if settings.value("/proxyEnabled", False):
        proxy = QNetworkProxy()
        proxyType = settings.value("/proxyType", 0)
        if proxyType in ["1", "Socks5Proxy"]:
            proxy.setType(QNetworkProxy.Socks5Proxy)
        elif proxyType in ["2", "NoProxy"]:
            proxy.setType(QNetworkProxy.NoProxy)
        elif proxyType in ["3", "HttpProxy"]:
            proxy.setType(QNetworkProxy.HttpProxy)
        elif proxyType in ["4", "HttpCachingProxy"] and QT_VERSION >= 0X040400:
            proxy.setType(QNetworkProxy.HttpCachingProxy)
        elif proxyType in ["5", "FtpCachingProxy"] and QT_VERSION >= 0X040400:
            proxy.setType(QNetworkProxy.FtpCachingProxy)
        else:
            proxy.setType(QNetworkProxy.DefaultProxy)
        proxy.setHostName(settings.value("/proxyHost"))
        proxy.setPort(settings.value("/proxyPort")[0])
        proxy.setUser(settings.value("/proxyUser"))
        proxy.setPassword(settings.value("/proxyPassword"))
        settings.endGroup()
        return proxy
