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

# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from qgis.core import *
from dialog_locator import DialogLocator
from utils import *
import psycopg2
import psycopg2.extras
import os.path
import sys


class Locator:
    
    global HOST, PORT, DB, USER, PWD
    global ZOOM_POINT_SCALE, STREET_LAYER, PORTAL_LAYER
    HOST = "localhost"
    PORT = 5432
    DB = "gesplan"
    USER = "roses"
    PWD = "pw_roses"
    
    # TODO: Configuration
    ZOOM_POINT_SCALE = 2000
    STREET_LAYER = "carrerer_eixos"
    PORTAL_LAYER = "carrerer_portals"
    STREET_ID = "ccar"
    STREET_NAME = "nombre"
    PORTAL_ID = "numero"
    PORTAL_STREET_ID = "carrer_id"
    

    def __init__(self, iface):
        
        global logger
                
        # Save reference to the QGIS interface
        self.iface = iface
        
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        
        # Enable logging
        logger = setLogger(__name__, self.plugin_dir + "/log", "logfile.log")    
        logger.setLevel(logging.DEBUG) 
        logger.debug('Plugin folder: ' + self.plugin_dir)
                
        # initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        localePath = os.path.join(self.plugin_dir, 'i18n', 'locator_{}.qm'.format(locale))
        if os.path.exists(localePath):
            self.translator = QTranslator()
            self.translator.load(localePath)
            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


    def initGui(self):
        
        logger.debug("initGUI")
        
        # Create action that will start plugin configuration
        icon = QIcon(os.path.dirname(__file__) + "/icons/icon.png")
        self.action = QAction(icon, u"Street Locator", self.iface.mainWindow())
        
        # connect the action to the run method
        self.action.triggered.connect(self.openForm)

        # Register function key
        self.iface.registerMainWindowAction(self.action, "F8")   
        
        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(u"&Street Locator", self.action)
        
        # Create the dialog (after translation) and keep reference
        self.dlg = DialogLocator()   
        if not self.dlg:        
            self.showMessageBar("UI form not loaded")            
            return
        
        # Connect buttons   
        QObject.connect(self.dlg.ui.btnSearch, SIGNAL("pressed()"), self.accept)          
        QObject.connect(self.dlg.ui.btnClose, SIGNAL("pressed()"), self.close)           
        
        # Connect to Database
        self.connectDb()    
        self.createConnection()
        
        # Set models
        self.modelStreet()   
            
        # Get street and portal layers
        self.getLayers()
        
        # Open form   
        self.dlg.setWindowTitle(u"Street Locator")
        self.dlg.move(10, 300)                  
        

    def openForm(self):
                
        logger.debug("openForm")
                        
        # Executed when function key or icon is pressed   
        global widgets   
             
        # Get widgets from form
        widgets = getWidgetsForm(self.dlg.ui)             
 
        # Show form
        self.dlg.show()   
        
        
    # Connect to Database    
    def connectDb(self):
        
        global conn, cursor
        try:
            conn = psycopg2.connect("host="+HOST+" port="+str(PORT)+" dbname="+DB+" user="+USER+" password="+PWD)              
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            setCursor(cursor)        
        except psycopg2.DatabaseError, e:
            logger.warning('Error %s' % e)
                
    
    def createConnection(self):
        
        self.db = QSqlDatabase.addDatabase("QPSQL");
        self.db.setHostName(HOST)
        self.db.setPort(PORT)
        self.db.setDatabaseName(DB)
        self.db.setUserName(USER)
        self.db.setPassword(PWD)
        if not self.db.open():
            logger.warning(self.db.lastError().text())
        
        
    def getLayers(self):
        
        layers = self.iface.legendInterface().layers()
        
        # Iterate over all layers. Check if they are vector, are visible
        for layer in layers:
            layerType = layer.type()
            logger.debug(layer.name())
            if layerType == QgsMapLayer.VectorLayer:
                visible = self.iface.legendInterface().isLayerVisible(layer)
                if visible and layer.name() == STREET_LAYER:
                    self.streetLayer = layer
                if visible and layer.name() == PORTAL_LAYER:
                    self.portalLayer = layer
                    
            
    def modelStreet(self):
             
        # Set SQL model              
        sql = "SELECT '' as ccar, '' as nombre "
        sql+= " UNION"             
        sql+= " SELECT ccar, nombre" 
        sql+= " FROM carrerer_eixos"
        sql+= " ORDER BY nombre" 
        logger.debug(sql) 
        self.model = QSqlQueryModel();
        self.model.setQuery(sql, self.db);
       
        # Set model to view
        self.dlg.ui.cboStreet.setModel(self.model)
        self.dlg.ui.cboStreet.setModelColumn(1)        
        completer = QCompleter(self.model)
        completer.setCompletionColumn(1)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setModel(self.model)
        completer.setMaxVisibleItems(10)
        self.dlg.ui.cboStreet.setCompleter(completer)   
        
        # Set signals
        self.dlg.ui.cboStreet.currentIndexChanged.connect(self.streetChanged)
        completer.activated.connect(self.streetChanged)
        
        
    def streetChanged(self, valor):        
                
        # Get ccar of selected street
        ccar = self.model.data(self.model.index(self.dlg.ui.cboStreet.currentIndex(), 0))
        name = self.dlg.ui.cboStreet.currentText()
        if (name == ''):
            self.dlg.ui.cboPortal.setModel(QSqlQueryModel())
            return
        
        # Get portals from selected street
        # Set SQL model   
        sql = "SELECT '' as numero, 0 as numero_n "
        sql+= " UNION"
        sql+= " SELECT numero, numero_n" 
        sql+= " FROM carrerer_portals"
        sql+= " WHERE carrer_id = '"+ccar+"'"
        sql+= " ORDER BY numero_n" 
        self.modelPortal = QSqlQueryModel();
        self.modelPortal.setQuery(sql, self.db);
        
        # Set model to view
        self.dlg.ui.cboPortal.setModel(self.modelPortal)
        self.dlg.ui.cboPortal.setModelColumn(0)        
        completer = QCompleter(self.modelPortal)
        completer.setModel(self.modelPortal)
        completer.setMaxVisibleItems(8)
        self.dlg.ui.cboPortal.setCompleter(completer)   
        
        # Set signals
        #self.dlg.ui.cboPortal.currentIndexChanged.connect(self.portalChanged)
        #completer.activated.connect(self.portalChanged)        
        
        
    def accept(self):    
       
        # Get selected street (and portal)
        ccar = self.model.data(self.model.index(self.dlg.ui.cboStreet.currentIndex(), 0))
        name = self.dlg.ui.cboStreet.currentText()
        if (name == ''):
            logger.info("Cap carrer especificat")
            return
        
        portal = self.dlg.ui.cboPortal.currentText()
        logger.debug(portal)    
        if (portal == ""):
            self.zoomToStreet(ccar)
        else:
            self.zoomToPortal(ccar, portal)
            
        
    def zoomToStreet(self, ccar):    
                     
        exp = "ccar = '"+ccar+"'"     
        self.setFilter(self.streetLayer, exp)          
        self.zoomToSelected(self.streetLayer)   
        self.portalLayer.removeSelection()   
                
          
    def zoomToPortal(self, ccar, portal):    
                     
        exp = "carrer_id = '"+ccar+"' AND numero = '"+portal+"'"     
        self.setFilter(self.portalLayer, exp)          
        
        # Zoom to point scale
        self.zoomToSelected(self.portalLayer)
        self.iface.mapCanvas().zoomScale(ZOOM_POINT_SCALE)    
        self.streetLayer.removeSelection()  
        
        
    def setFilter(self, layer, exp):

        # Clear current selection
        layer.removeSelection()
        
        exp = QgsExpression(exp)
        if exp.hasParserError():
            logger.warning("Expression Error: "+str(exp.parserErrorString()))
            return
        
        # Select features that matches expression      
        selection = []  
        exp.prepare(layer.pendingFields())
        features = filter(exp.evaluate, layer.getFeatures())
        for feature in features:
            selection.append(feature.id())
        layer.setSelectedFeatures(selection)                              
        

    def zoomToSelected(self, layer):
                
        box = layer.boundingBoxOfSelected()
        self.iface.mapCanvas().setExtent(box)
        self.iface.mapCanvas().refresh() 
                         
                            
    def close(self):
        
        self.dlg.setVisible(False);
        

    def unload(self):
        
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu(u"&Street Locator", self.action)
        self.iface.removeToolBarIcon(self.action)

        
