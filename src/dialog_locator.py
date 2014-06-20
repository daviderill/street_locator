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

from PyQt4 import QtGui
from ui_locator import Ui_Dialog


class DialogLocator(QtGui.QDialog):
    
    def __init__(self):
        
        QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        #self.setupUi(self)
        
        # Set up the user interface from Designer.
        self.ui = Ui_Dialog()   
        self.ui.setupUi(self) 
