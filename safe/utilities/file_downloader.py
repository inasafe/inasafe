# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
  **IS Utilities implementation.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

import logging

from qgis.core import QgsApplication, QgsNetworkAccessManager
# noinspection PyPackageRequirements
from qgis.PyQt.QtCore import QByteArray, QFile, QUrl
# noinspection PyPackageRequirements
from qgis.PyQt.QtNetwork import QNetworkReply, QNetworkRequest

from safe.common.utilities import humanize_file_size
from safe.utilities.i18n import tr


__author__ = 'akbargumbira@gmail.com'
__revision__ = '$Format:%H$'
__date__ = '16/03/2014'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')


LOGGER = logging.getLogger('InaSAFE')


class FileDownloader():

    """The blueprint for downloading file from url."""

    def __init__(self, url, output_path, progress_dialog=None):
        """Constructor of the class.

        .. versionchanged:: 3.3 removed manager parameter.

        :param url: URL of file.
        :type url: str

        :param output_path: Output path.
        :type output_path: str

        :param progress_dialog: Progress dialog widget.
        :type progress_dialog: QWidget
        """
        # noinspection PyArgumentList
        self.manager = QgsNetworkAccessManager.instance()
        self.url = QUrl(url)
        self.output_path = output_path
        self.progress_dialog = progress_dialog
        if self.progress_dialog:
            self.prefix_text = self.progress_dialog.labelText()
        self.output_file = None
        self.reply = None
        self.downloaded_file_buffer = None
        self.finished_flag = False

    def download(self):
        """Downloading the file.

        :returns: True if success, otherwise returns a tuple with format like
            this (QNetworkReply.NetworkError, error_message)

        :raises: IOError - when cannot create output_path
        """
        # Prepare output path
        self.output_file = QFile(self.output_path)
        if not self.output_file.open(QFile.WriteOnly):
            raise IOError(self.output_file.errorString())

        # Prepare downloaded buffer
        self.downloaded_file_buffer = QByteArray()

        # Request the url
        request = QNetworkRequest(self.url)
        self.reply = self.manager.get(request)
        self.reply.readyRead.connect(self.get_buffer)
        self.reply.finished.connect(self.write_data)
        self.manager.requestTimedOut.connect(self.request_timeout)

        if self.progress_dialog:
            # progress bar
            def progress_event(received, total):
                """Update progress.

                :param received: Data received so far.
                :type received: int

                :param total: Total expected data.
                :type total: int
                """
                # noinspection PyArgumentList
                QgsApplication.processEvents()

                self.progress_dialog.adjustSize()

                human_received = humanize_file_size(received)
                human_total = humanize_file_size(total)

                label_text = tr("%s : %s of %s" % (
                    self.prefix_text, human_received, human_total))

                self.progress_dialog.setLabelText(label_text)
                self.progress_dialog.setMaximum(total)
                self.progress_dialog.setValue(received)

            # cancel
            def cancel_action():
                """Cancel download."""
                self.reply.abort()
                self.reply.deleteLater()

            self.reply.downloadProgress.connect(progress_event)
            self.progress_dialog.canceled.connect(cancel_action)

        # Wait until finished
        # On Windows 32bit AND QGIS 2.2, self.reply.isFinished() always
        # returns False even after finished slot is called. So, that's why we
        # are adding self.finished_flag (see #864)
        while not self.reply.isFinished() and not self.finished_flag:
            # noinspection PyArgumentList
            QgsApplication.processEvents()

        result = self.reply.error()
        try:
            http_code = int(self.reply.attribute(
                QNetworkRequest.HttpStatusCodeAttribute))
        except TypeError:
            # If the user cancels the request, the HTTP response will be None.
            http_code = None

        self.reply.abort()
        self.reply.deleteLater()

        if result == QNetworkReply.NoError:
            return True, None

        elif result == QNetworkReply.UnknownNetworkError:
            return False, tr(
                'The network is unreachable. Please check your internet '
                'connection.')

        elif http_code == 408:
            msg = tr(
                'Sorry, the server aborted your request. '
                'Please try a smaller area.')
            LOGGER.debug(msg)
            return False, msg

        elif http_code == 509:
            msg = tr(
                'Sorry, the server is currently busy with another request. '
                'Please try again in a few minutes.')
            LOGGER.debug(msg)
            return False, msg

        elif result == QNetworkReply.ProtocolUnknownError or \
                result == QNetworkReply.HostNotFoundError:
            LOGGER.exception('Host not found : %s' % self.url.encodedHost())
            return False, tr(
                'Sorry, the server is unreachable. Please try again later.')

        elif result == QNetworkReply.ContentNotFoundError:
            LOGGER.exception('Path not found : %s' % self.url.path())
            return False, tr('Sorry, the layer was not found on the server.')

        else:
            return result, self.reply.errorString()

    def get_buffer(self):
        """Get buffer from self.reply and store it to our buffer container."""
        buffer_size = self.reply.size()
        data = self.reply.read(buffer_size)
        self.downloaded_file_buffer.append(data)

    def write_data(self):
        """Write data to a file."""
        self.output_file.write(self.downloaded_file_buffer)
        self.output_file.close()
        self.finished_flag = True

    def request_timeout(self):
        """The request timed out."""
        if self.progress_dialog:
            self.progress_dialog.hide()
