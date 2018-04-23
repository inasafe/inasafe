# coding=utf-8
"""Fonts which are used in InaSAFE."""

from qgis.PyQt.QtGui import QFont

big_font = QFont()
big_font.setPointSize(80)

bold_font = QFont()
bold_font.setItalic(True)
bold_font.setBold(True)
bold_font.setWeight(75)
