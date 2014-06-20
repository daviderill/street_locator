# -*- coding: utf-8 -*-
"""
/***************************************************************************
 StreetLocator
                                 A QGIS plugin
 Street Locator
                              -------------------
        begin                : 2014-06-19
        copyright            : (C) 2014 by David Erill
        email                : daviderill79@gmail.com
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

def classFactory(iface):
    # load Locator class from file locator
    from locator import Locator
    return Locator(iface)