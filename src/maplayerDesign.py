# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'kml_generator.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

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

class Ui_FormKml(object):
    def setupUi(self, FormKml):
        FormKml.setObjectName(_fromUtf8("FormKml"))
        FormKml.resize(392, 124)
        FormKml.setMinimumSize(QtCore.QSize(392, 0))
        self.verticalLayout_2 = QtGui.QVBoxLayout(FormKml)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(FormKml)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.toolButton_input = QtGui.QToolButton(FormKml)
        self.toolButton_input.setEnabled(True)
        self.toolButton_input.setMinimumSize(QtCore.QSize(50, 0))
        self.toolButton_input.setStatusTip(_fromUtf8(""))
        self.toolButton_input.setObjectName(_fromUtf8("toolButton_input"))
        self.horizontalLayout.addWidget(self.toolButton_input)
        self.lineEdit_input = QtGui.QLineEdit(FormKml)
        self.lineEdit_input.setEnabled(True)
        self.lineEdit_input.setMinimumSize(QtCore.QSize(200, 18))
        self.lineEdit_input.setMaximumSize(QtCore.QSize(200, 18))
        self.lineEdit_input.setText(_fromUtf8(""))
        self.lineEdit_input.setReadOnly(True)
        self.lineEdit_input.setObjectName(_fromUtf8("lineEdit_input"))
        self.horizontalLayout.addWidget(self.lineEdit_input)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_2 = QtGui.QLabel(FormKml)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_2.addWidget(self.label_2)
        self.toolButton_output = QtGui.QToolButton(FormKml)
        self.toolButton_output.setMinimumSize(QtCore.QSize(50, 0))
        self.toolButton_output.setObjectName(_fromUtf8("toolButton_output"))
        self.horizontalLayout_2.addWidget(self.toolButton_output)
        self.lineEdit_output = QtGui.QLineEdit(FormKml)
        self.lineEdit_output.setEnabled(True)
        self.lineEdit_output.setMinimumSize(QtCore.QSize(200, 18))
        self.lineEdit_output.setMaximumSize(QtCore.QSize(200, 18))
        self.lineEdit_output.setReadOnly(True)
        self.lineEdit_output.setObjectName(_fromUtf8("lineEdit_output"))
        self.horizontalLayout_2.addWidget(self.lineEdit_output)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.pushButton_OK = QtGui.QPushButton(FormKml)
        self.pushButton_OK.setObjectName(_fromUtf8("pushButton_OK"))
        self.horizontalLayout_3.addWidget(self.pushButton_OK)
        self.pushButton_Cancel = QtGui.QPushButton(FormKml)
        self.pushButton_Cancel.setObjectName(_fromUtf8("pushButton_Cancel"))
        self.horizontalLayout_3.addWidget(self.pushButton_Cancel)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.progressBar = QtGui.QProgressBar(FormKml)
        self.progressBar.setStyleSheet(_fromUtf8("text-align: center"))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.verticalLayout_2.addWidget(self.progressBar)
        self.retranslateUi(FormKml)
        QtCore.QMetaObject.connectSlotsByName(FormKml)

    def retranslateUi(self, FormKml):
        FormKml.setWindowTitle(_translate("FormKmz", "KML Generator", None))
        self.label.setText(_translate("FormKmz", "Input CSV file: ", None))
        self.toolButton_input.setToolTip(_translate("FormKmz", "Select measurement log file", None))
        self.toolButton_input.setText(_translate("FormKmz", "...", None))
        self.label_2.setText(_translate("FormKmz", "Output KML file: ", None))
        self.toolButton_output.setToolTip(_translate("FormKmz", "Select the output file", None))
        self.toolButton_output.setText(_translate("FormKmz", "...", None))
        self.pushButton_OK.setText(_translate("FormKmz", "OK", None))
        self.pushButton_Cancel.setText(_translate("FormKmz", "Cancel", None))
