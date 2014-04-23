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

__author__ = 'akbargumbira@gmail.com'
__revision__ = '$Format:%H$'
__date__ = '16/03/2014'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')


#noinspection PyPackageRequirements
from PyQt4.QtCore import QCoreApplication, QFile, QUrl, QByteArray
#noinspection PyPackageRequirements
from PyQt4.QtNetwork import QNetworkRequest, QNetworkReply


class FileDownloader(object):
    """The blueprint for downloading file from url."""
    def __init__(self, manager, url, output_path, progress_dialog=None):
        """Constructor of the class.

        :param manager: QNetworkAccessManager instance to handle downloading.
        :type manager: QNetworkAccessManager

        :param url: URL of file.
        :type url: str

        :param output_path: Output path.
        :type output_path: str

        :param progress_dialog: Progress dialog widget.
        :type progress_dialog: QWidget

        """
        self.manager = manager
        self.url = url
        self.output_path = output_path
        self.progress_dialog = progress_dialog
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
        request = QNetworkRequest(QUrl(self.url))
        self.reply = self.manager.get(request)
        self.reply.readyRead.connect(self.get_buffer)
        self.reply.finished.connect(self.write_data)

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
                QCoreApplication.processEvents()

                label_text = "%s / %s" % (received, total)
                self.progress_dialog.setLabelText(label_text)
                self.progress_dialog.setMaximum(total)
                self.progress_dialog.setValue(received)

            # cancel
            def cancel_action():
                """Cancel download."""
                self.reply.abort()

            self.reply.downloadProgress.connect(progress_event)
            self.progress_dialog.canceled.connect(cancel_action)

        # Wait until finished
        # On Windows 32bit AND QGIS 2.2, self.reply.isFinished() always
        # returns False even after finished slot is called. So, that's why we
        # are adding self.finished_flag (see #864)
        while not self.reply.isFinished() and not self.finished_flag:
            # noinspection PyArgumentList
            QCoreApplication.processEvents()

        result = self.reply.error()
        if result == QNetworkReply.NoError:
            return True, None
        else:
            return result, str(self.reply.errorString())

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
