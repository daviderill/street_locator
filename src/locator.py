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
from qgis.gui import QgsMessageBar
from dialog_locator import DialogLocator
from utils import *
import os.path


class Locator:
    
    global MSG_DURATION, ZOOM_POINT_SCALE, PROP_NAME
    
    MSG_DURATION = 5
    ZOOM_POINT_SCALE = 2000
    PROP_NAME = "street.properties"
    

    def __init__(self, iface):
        
        global logger
                
        # Save reference to the QGIS interface
        self.iface = iface
        
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        
        # Enable logging
        logger = setLogger(__name__, self.plugin_dir+"/log", "logfile.log")    
        logger.info('Plugin folder: '+self.plugin_dir)
                
        # initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        localePath = os.path.join(self.plugin_dir, 'i18n', 'locator_{}.qm'.format(locale))
        if os.path.exists(localePath):
            self.translator = QTranslator()
            self.translator.load(localePath)
            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)
                
        self.streetDict = {}  
        self.layersList = []   
        self.proj = None  
        self.propDict = {}  
        self.show = True   


    def initGui(self): 
        
        # Create action that will start plugin configuration
        icon = QIcon(os.path.dirname(__file__)+"/icons/icon.png")
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
            self.showMessageBar("No s'ha pogut carregar el formulari de l'extensió Street Locator")            
            return
        
        # Load properties file
        #self.loadPropFile()
        
        # Set scales zoom
        self.setScalesZoom()
        
        # Set signals of widgets  
        QObject.connect(self.dlg.ui.btnSearchStreet, SIGNAL("pressed()"), self.searchStreet)          
        QObject.connect(self.dlg.ui.btnSearch, SIGNAL("pressed()"), self.searchPortal)          
        QObject.connect(self.dlg.ui.btnClose, SIGNAL("pressed()"), self.close)           
        QObject.connect(self.dlg.ui.btnSave, SIGNAL("pressed()"), self.saveConfigPressed)           
        self.dlg.ui.cboStreetLayer.currentIndexChanged.connect(self.streetLayerChanged)   
        self.dlg.ui.cboPortalLayer.currentIndexChanged.connect(self.portalLayerChanged)   
        
        # Open form   
        self.dlg.setWindowTitle(u"Street Locator")
        self.dlg.move(10, 300)                  
        
        
    def loadPropFile(self):
        
        # Get current .qgs path. Then custom and default .properties file
        proj = QgsProject.instance()
        self.streetProp = proj.homePath()+"/"+PROP_NAME
        logger.info("Project folder: "+proj.homePath())  
        
        # Open .properties file and load parameters in a dictionary
        if not os.path.isfile(self.streetProp):
            self.showInfo("No s'ha trobat el fitxer de configuració: "+self.streetProp, MSG_DURATION)
            self.dlg.ui.toolBox.setCurrentIndex(1)
            return   
        
        #fileProp = open(self.streetProp, 'r')
        self.propDict = dict(line.strip().split('=') for line in open(self.streetProp))
        
        # Set Configuration panel
        setTextCombo(self.dlg.ui.cboStreetLayer, self.propDict["STREET_LAYER"])
        setTextCombo(self.dlg.ui.cboStreetCode, self.propDict["STREET_CODE"])
        setTextCombo(self.dlg.ui.cboStreetName, self.propDict["STREET_NAME"])
        setTextCombo(self.dlg.ui.cboPortalLayer, self.propDict["PORTAL_LAYER"])
        setTextCombo(self.dlg.ui.cboPortalCode, self.propDict["PORTAL_CODE"])
        setTextCombo(self.dlg.ui.cboPortalNumber, self.propDict["PORTAL_NUMBER"])
        self.saveConfigPressed()
                       

    # Executed when function key or icon is pressed       
    def openForm(self):
                                                                     
        # Get all layers (only first time)
        if len(self.layersList) == 0:
            self.getLayers()    
            # TODO: Load properties file (only first time)
            self.loadPropFile()                    
 
        # Show form
        self.dlg.show()   
        self.dlg.activateWindow();
            
        
    def setScalesZoom(self):
        
        self.dlg.ui.cboScaleZoom.addItem("500")
        self.dlg.ui.cboScaleZoom.addItem("1000")
        self.dlg.ui.cboScaleZoom.addItem("2000")
        self.dlg.ui.cboScaleZoom.addItem("5000")
        self.dlg.ui.cboScaleZoom.addItem("10000")
        self.dlg.ui.cboScaleZoom.setCurrentIndex(2)
        
        
    def getLayers(self):
        
        logger.info("getLayers")
        
        self.dlg.ui.cboStreetLayer.addItem("")
        self.dlg.ui.cboPortalLayer.addItem("")
        self.layers = self.iface.legendInterface().layers()
        
        # Iterate over all layers
        for layer in self.layers:
            layerType = layer.type()
            logger.debug(layer.name())
            # Check if they are vector
            if layerType == QgsMapLayer.VectorLayer:
                self.layersList.append(layer)
                self.dlg.ui.cboStreetLayer.addItem(layer.name())
                self.dlg.ui.cboPortalLayer.addItem(layer.name()) 
        

    def streetChanged(self, valor):      
        
        name = self.dlg.ui.cboStreet.currentText()
        if (name == ''):
            return
        
        # Get portals from selected street code
        selectedStreetCode = [key for key, value in self.streetDict.iteritems() if value == name][0]        
        self.listPortalNumber = [""]
        for feature in self.portalLayer.getFeatures(): 
            if feature[self.portalCode] == selectedStreetCode: 
                self.listPortalNumber.append(feature[self.portalNumber])
             
        self.listPortalNumber.sort()         
        model = QStringListModel()
        model.setStringList(self.listPortalNumber)  
        completer = QCompleter()
        completer.setCompletionColumn(0)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setModel(model)
        completer.setMaxVisibleItems(10)
        self.dlg.ui.cboPortal.setModel(model)   
        self.dlg.ui.cboPortal.setCompleter(completer) 
                
     
    def searchStreet(self):    
       
        # Get selected street (and portal)
        name = self.dlg.ui.cboStreet.currentText()
        if (name == ''):
            logger.info("Cap carrer especificat")
            return
        if len(self.streetDict) == 0:
            logger.info("No s'ha trobat cap carrer")
            return        
        ccar = [key for key, value in self.streetDict.iteritems() if value == name][0]
        
        self.zoomToStreet(str(ccar))
            
            
    def searchPortal(self):    
       
        # Get selected street (and portal)
        name = self.dlg.ui.cboStreet.currentText()
        if (name == ''):
            logger.info("Cap carrer especificat")
            return
        if len(self.streetDict) == 0:
            logger.info("No s'ha trobat cap carrer")
            return
        #ccar = self.model.data(self.model.index(self.dlg.ui.cboStreet.currentIndex(), 0))
        ccar = [key for key, value in self.streetDict.iteritems() if value == name][0]
        
        portal = self.dlg.ui.cboPortal.currentText()
        logger.debug(portal)    
        if (portal == ""):
            self.zoomToStreet(str(ccar))
        else:
            self.zoomToPortal(str(ccar), portal)
            
        
    def zoomToStreet(self, ccar):    
                     
        #exp = "ccar = '"+ccar+"'"     
        exp = self.streetCode+" = '"+ccar+"'"     
        self.setFilter(self.streetLayer, exp)          
        self.zoomToSelected(self.streetLayer)   
        self.portalLayer.removeSelection()   
                
          
    def zoomToPortal(self, ccar, portal):    
                     
        #exp = "carrer_id = '"+ccar+"' AND numero = '"+portal+"'"     
        exp = self.portalCode+" = '"+ccar+"' AND "+self.portalNumber+" = '"+portal+"'"     
        self.setFilter(self.portalLayer, exp)          
        
        # Zoom to point scale
        self.zoomToSelected(self.portalLayer)
        scale = self.dlg.ui.cboScaleZoom.currentText()
        self.iface.mapCanvas().zoomScale(int(scale))    
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
                         
                         
    # Configuration signals           
    def streetLayerChanged(self):   
        
        streetLayerName = self.dlg.ui.cboStreetLayer.currentText()
        self.dlg.ui.cboStreetCode.clear()
        self.dlg.ui.cboStreetName.clear()
        if (streetLayerName != ""):
            self.dlg.ui.cboStreetCode.addItem("")
            self.dlg.ui.cboStreetName.addItem("")
            self.streetLayer = self.getLayerByName(streetLayerName)
            # Get fields of selected layer
            for field in self.streetLayer.dataProvider().fields():
                self.dlg.ui.cboStreetCode.addItem(field.name())
                self.dlg.ui.cboStreetName.addItem(field.name())        
        
        
    def portalLayerChanged(self):   
                
        portalLayerName = self.dlg.ui.cboPortalLayer.currentText()
        self.dlg.ui.cboPortalCode.clear()
        self.dlg.ui.cboPortalNumber.clear()
        if (portalLayerName != ""):
            self.dlg.ui.cboPortalCode.addItem("")
            self.dlg.ui.cboPortalNumber.addItem("")
            self.portalLayer = self.getLayerByName(portalLayerName)
            # Get fields of selected layer
            for field in self.portalLayer.dataProvider().fields():
                self.dlg.ui.cboPortalCode.addItem(field.name())
                self.dlg.ui.cboPortalNumber.addItem(field.name())    
                        
        
    def getLayerByName(self, layerName):
        
        for layer in self.layers:
            logger.debug(layer.name())
            if layer.name() == layerName:
                return layer
                    
                    
    def saveConfigPressed(self):
        
        if self.saveConfig():
            self.showInfo(u"Fitxer de configuració carregat correctament: "+self.streetProp, MSG_DURATION)
            self.dlg.ui.toolBox.setCurrentIndex(0)
        else:
            self.dlg.ui.toolBox.setCurrentIndex(1)      
              

    def saveConfig(self):    
        
        self.dlg.ui.cboStreet.clear()
        self.streetCode = self.dlg.ui.cboStreetCode.currentText()
        self.streetName = self.dlg.ui.cboStreetName.currentText()
        self.portalCode = self.dlg.ui.cboPortalCode.currentText()
        self.portalNumber = self.dlg.ui.cboPortalNumber.currentText()
        if (self.streetCode == ''):
            self.showWarning(u"Cal especificar camp que conté el codi del carrer", MSG_DURATION)
            return False
        if (self.streetName == ''):
            self.showWarning(u"Cal especificar camp que conté el nom del carrer", MSG_DURATION)
            return False
        if (self.portalCode == ''):
            self.showWarning(u"Cal especificar camp que conté l'enllaç al codi del carrer", MSG_DURATION)
            return False
        if (self.portalNumber == ''):
            self.showWarning(u"Cal especificar camp que conté el número de policia", MSG_DURATION)
            return False
        logger.info("streetCode: "+self.streetCode+" - streetName: "+self.streetName)
        logger.info("portalCode: "+self.portalCode+" - portalNumber: "+self.portalNumber)
        
        self.listStreetCode = [""]
        self.listStreetName = [""]
        for feature in self.streetLayer.getFeatures():   
            self.listStreetCode.append(feature[self.streetCode])
            self.listStreetName.append(feature[self.streetName])
            self.streetDict[feature[self.streetCode]] = feature[self.streetName]
             
        self.listStreetName.sort()         
        model = QStringListModel()
        model.setStringList(self.listStreetName)  
        completer = QCompleter()
        #completer.setCompletionColumn(0)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setModel(model)
        completer.setMaxVisibleItems(10)
        self.dlg.ui.cboStreet.setModel(model)   
        self.dlg.ui.cboStreet.setCompleter(completer) 
        
        # Set signals
        self.dlg.ui.cboStreet.currentIndexChanged.connect(self.streetChanged)
        completer.activated.connect(self.streetChanged)       
        return True     
              
              
    def showInfo(self, text, duration = None):
        
        if self.show:
            if duration is None:
                self.iface.messageBar().pushMessage("", text, QgsMessageBar.INFO)  
            else:
                self.iface.messageBar().pushMessage("", text, QgsMessageBar.INFO, duration)              
        logger.info(text)    
        
          
    def showWarning(self, text, duration = None):
        
        if self.show:
            if duration is None:
                self.iface.messageBar().pushMessage("", text, QgsMessageBar.WARNING)  
            else:
                self.iface.messageBar().pushMessage("", text, QgsMessageBar.WARNING, duration)              
        logger.warning(text)    
                                        
                                
    def close(self):
        
        self.dlg.setVisible(False);
        

    def unload(self):
        
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu(u"&Street Locator", self.action)
        self.iface.removeToolBarIcon(self.action)

        
