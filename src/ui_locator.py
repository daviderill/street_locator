# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_locator.ui'
#
# Created: Fri Jun 20 15:34:49 2014
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(387, 213)
        self.lblTitle = QtGui.QLabel(Dialog)
        self.lblTitle.setGeometry(QtCore.QRect(20, 10, 200, 21))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Segoe UI"))
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        font.setKerning(True)
        self.lblTitle.setFont(font)
        self.lblTitle.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.lblTitle.setWordWrap(True)
        self.lblTitle.setObjectName(_fromUtf8("lblTitle"))
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(20, 50, 111, 21))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Segoe UI"))
        font.setPointSize(9)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(20, 80, 121, 21))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Segoe UI"))
        font.setPointSize(9)
        self.label_3.setFont(font)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.btnSearch = QtGui.QPushButton(Dialog)
        self.btnSearch.setGeometry(QtCore.QRect(220, 170, 71, 25))
        self.btnSearch.setLocale(QtCore.QLocale(QtCore.QLocale.Catalan, QtCore.QLocale.Spain))
        self.btnSearch.setObjectName(_fromUtf8("btnSearch"))
        self.btnClose = QtGui.QPushButton(Dialog)
        self.btnClose.setGeometry(QtCore.QRect(300, 170, 71, 25))
        self.btnClose.setLocale(QtCore.QLocale(QtCore.QLocale.Catalan, QtCore.QLocale.Spain))
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.cboStreet = QtGui.QComboBox(Dialog)
        self.cboStreet.setGeometry(QtCore.QRect(130, 50, 241, 22))
        self.cboStreet.setEditable(True)
        self.cboStreet.setModelColumn(0)
        self.cboStreet.setObjectName(_fromUtf8("cboStreet"))
        self.cboPortal = QtGui.QComboBox(Dialog)
        self.cboPortal.setGeometry(QtCore.QRect(130, 80, 91, 22))
        self.cboPortal.setEditable(True)
        self.cboPortal.setObjectName(_fromUtf8("cboPortal"))

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.lblTitle.setText(_translate("Dialog", "Carrerer", None))
        self.label.setText(_translate("Dialog", "Seleccionar carrer:", None))
        self.label_3.setText(_translate("Dialog", "Seleccionar portal:", None))
        self.btnSearch.setText(_translate("Dialog", "Cercar", None))
        self.btnClose.setText(_translate("Dialog", "Sortir", None))

