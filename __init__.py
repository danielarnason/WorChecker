# -*- coding: utf-8 -*-
"""
/***************************************************************************
 WorChecker
                                 A QGIS plugin
 Dette plugin viser, hvilke filer et MapInfo workspace  refererer til.
                             -------------------
        begin                : 2018-08-06
        copyright            : (C) 2018 by Daníel Örn Árnason
        email                : daniel.arnason@egekom.dk
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load WorChecker class from file WorChecker.

    :param iface: A QGIS interface instance.
    :type iface: QgisInterface
    """
    #
    from .wor_checker import WorChecker
    return WorChecker(iface)
