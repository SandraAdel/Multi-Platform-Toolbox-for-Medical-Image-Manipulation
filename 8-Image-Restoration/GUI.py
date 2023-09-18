# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Task8_GUI_1.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1061, 781)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.noiseTypeComboBox = QtWidgets.QComboBox(self.centralwidget)
        self.noiseTypeComboBox.setGeometry(QtCore.QRect(120, 30, 131, 31))
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(9)
        self.noiseTypeComboBox.setFont(font)
        self.noiseTypeComboBox.setObjectName("noiseTypeComboBox")
        self.noiseTypeComboBox.addItem("")
        self.noiseTypeComboBox.addItem("")
        self.noiseTypeComboBox.addItem("")
        self.gridLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(30, 130, 301, 271))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.originalImageGridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.originalImageGridLayout.setContentsMargins(0, 0, 0, 0)
        self.originalImageGridLayout.setObjectName("originalImageGridLayout")
        self.originalImageLabel = QtWidgets.QLabel(self.centralwidget)
        self.originalImageLabel.setGeometry(QtCore.QRect(120, 90, 141, 31))
        font = QtGui.QFont()
        font.setFamily("Script MT Bold")
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.originalImageLabel.setFont(font)
        self.originalImageLabel.setObjectName("originalImageLabel")
        self.noisyImageLabel = QtWidgets.QLabel(self.centralwidget)
        self.noisyImageLabel.setGeometry(QtCore.QRect(470, 90, 121, 41))
        font = QtGui.QFont()
        font.setFamily("Script MT Bold")
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.noisyImageLabel.setFont(font)
        self.noisyImageLabel.setObjectName("noisyImageLabel")
        self.gridLayoutWidget_2 = QtWidgets.QWidget(self.centralwidget)
        self.gridLayoutWidget_2.setGeometry(QtCore.QRect(380, 130, 301, 271))
        self.gridLayoutWidget_2.setObjectName("gridLayoutWidget_2")
        self.noisyImageGridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget_2)
        self.noisyImageGridLayout.setContentsMargins(0, 0, 0, 0)
        self.noisyImageGridLayout.setObjectName("noisyImageGridLayout")
        self.gridLayoutWidget_4 = QtWidgets.QWidget(self.centralwidget)
        self.gridLayoutWidget_4.setGeometry(QtCore.QRect(110, 470, 531, 271))
        self.gridLayoutWidget_4.setObjectName("gridLayoutWidget_4")
        self.ROIHistogramGridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget_4)
        self.ROIHistogramGridLayout.setContentsMargins(0, 0, 0, 0)
        self.ROIHistogramGridLayout.setObjectName("ROIHistogramGridLayout")
        self.ROIMeanLabel = QtWidgets.QLabel(self.centralwidget)
        self.ROIMeanLabel.setGeometry(QtCore.QRect(730, 550, 141, 31))
        font = QtGui.QFont()
        font.setFamily("Script MT Bold")
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.ROIMeanLabel.setFont(font)
        self.ROIMeanLabel.setObjectName("ROIMeanLabel")
        self.ROIStandardDeviationLabel = QtWidgets.QLabel(self.centralwidget)
        self.ROIStandardDeviationLabel.setGeometry(QtCore.QRect(670, 620, 231, 31))
        font = QtGui.QFont()
        font.setFamily("Script MT Bold")
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.ROIStandardDeviationLabel.setFont(font)
        self.ROIStandardDeviationLabel.setObjectName("ROIStandardDeviationLabel")
        self.ROIMeanData = QtWidgets.QLabel(self.centralwidget)
        self.ROIMeanData.setGeometry(QtCore.QRect(910, 550, 131, 31))
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.ROIMeanData.setFont(font)
        self.ROIMeanData.setObjectName("ROIMeanData")
        self.gridLayoutWidget_3 = QtWidgets.QWidget(self.centralwidget)
        self.gridLayoutWidget_3.setGeometry(QtCore.QRect(730, 130, 301, 271))
        self.gridLayoutWidget_3.setObjectName("gridLayoutWidget_3")
        self.selectedROIImageGridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget_3)
        self.selectedROIImageGridLayout.setContentsMargins(0, 0, 0, 0)
        self.selectedROIImageGridLayout.setObjectName("selectedROIImageGridLayout")
        self.selectedROILabel = QtWidgets.QLabel(self.centralwidget)
        self.selectedROILabel.setGeometry(QtCore.QRect(820, 90, 131, 41))
        font = QtGui.QFont()
        font.setFamily("Script MT Bold")
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.selectedROILabel.setFont(font)
        self.selectedROILabel.setObjectName("selectedROILabel")
        self.ROIHistogramLabel = QtWidgets.QLabel(self.centralwidget)
        self.ROIHistogramLabel.setGeometry(QtCore.QRect(310, 430, 141, 31))
        font = QtGui.QFont()
        font.setFamily("Script MT Bold")
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.ROIHistogramLabel.setFont(font)
        self.ROIHistogramLabel.setObjectName("ROIHistogramLabel")
        self.ROIStandardDeviationData = QtWidgets.QLabel(self.centralwidget)
        self.ROIStandardDeviationData.setGeometry(QtCore.QRect(910, 620, 131, 31))
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.ROIStandardDeviationData.setFont(font)
        self.ROIStandardDeviationData.setObjectName("ROIStandardDeviationData")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.noiseTypeComboBox.setItemText(0, _translate("MainWindow", "Choose Noise Type"))
        self.noiseTypeComboBox.setItemText(1, _translate("MainWindow", "Gaussian Noise"))
        self.noiseTypeComboBox.setItemText(2, _translate("MainWindow", "Uniform Noise"))
        self.originalImageLabel.setText(_translate("MainWindow", "Original Image"))
        self.noisyImageLabel.setText(_translate("MainWindow", "Noisy Image"))
        self.ROIMeanLabel.setText(_translate("MainWindow", "ROI Mean:"))
        self.ROIStandardDeviationLabel.setText(_translate("MainWindow", "ROI Standard Deviation:"))
        self.ROIMeanData.setText(_translate("MainWindow", " "))
        self.selectedROILabel.setText(_translate("MainWindow", "Selected ROI"))
        self.ROIHistogramLabel.setText(_translate("MainWindow", "ROI Histogram"))
        self.ROIStandardDeviationData.setText(_translate("MainWindow", " "))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
