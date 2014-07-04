from PyQt4.QtCore import *
from PyQt4.QtGui import *
import inspect
import imp
import logging
import os.path

#	
# Utility funcions	
#
def setTextCombo(combo, text):
    index = combo.findText(text)
    if index > -1:
        combo.setCurrentIndex(index)
    
    
def getWidgetsForm(form):
    
    # Get dialog widgets
    for name, data in inspect.getmembers(form):
        if name == '__dict__':
            return data


def loadClass(filepath, classname):
    
    class_inst = None
    mod_name,file_ext = os.path.splitext(os.path.split(filepath)[-1])

    if file_ext.lower() == '.py':
        py_mod = imp.load_source(mod_name, filepath)

    elif file_ext.lower() == '.pyc':
        py_mod = imp.load_compiled(mod_name, filepath)

    if hasattr(py_mod, classname):
        class_inst = getattr(py_mod, classname)()

    return class_inst    


def getClassName(module):
    
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj):
            return name          
    
    
def setLogger(name, folder, filename):
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # create file handler
    if not os.path.exists(folder):
        os.makedirs(folder)
    filepath = folder + "/" + filename 
    fh = logging.FileHandler(filepath)
    fh.setLevel(logging.INFO)
    
    # create console handler
    #ch = logging.StreamHandler()
    #ch.setLevel(logging.INFO)
    
    # create formatter and add it to the handlers
    formatter_fh = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    #formatter_ch = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter_fh)
    #ch.setFormatter(formatter_ch)
    
    # add the handlers to logger
    if (len(logger.handlers) > 0):  
        removeHandlers(logger) 
    logger.addHandler(fh)
    #logger.addHandler(ch)   
    
    return logger
    
    
def removeHandlers(logger):    
    
    #logger.info('Total: %d'%len(logger.handlers))    
    for h in logger.handlers:
        #logger.info('removing handler %s'%str(h))
        logger.removeHandler(h)     
        