
                                                                    # # # # # # # # # # Imports # # # # # # # # # #

import sys
import cv2
import os.path
from PIL import Image
from pydicom import dcmread
from PyQt5 import QtWidgets
from GUI import Ui_MainWindow
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


                                                                # # # # # # # # # # Window Declaration # # # # # # # # # #


class MainWindow(QMainWindow):

    # Window Constructor
    def __init__(self):

        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

                                                        # # # # # # # # # # Class Variables Initialization # # # # # # # # # #

        # Categorising UI Elements, Consisting of Image Info Titles and Data Itself, into General Image Info and DICOM Related Ones
        self.generalImageInfoLabels = [self.ui.imageSizeTitleLabel, self.ui.imageSizeDataLabel, self.ui.imageBitsTitleLabel, self.ui.imageBitsDataLabel, 
                                       self.ui.imageBitDepthTitleLabel, self.ui.imageBitDepthDataLabel, self.ui.imageColorTitleLabel, self.ui.imageColorDataLabel]
        self.dicomSpecificImageInfoLabels = [self.ui.usedModalityTitleLabel, self.ui.usedModalityDataLabel, self.ui.patientNameTitleLabel, self.ui.patientNameDataLabel, 
                                             self.ui.patientAgeTitleLabel, self.ui.patientAgeDataLabel, self.ui.bodyPartTitleLabel, self.ui.bodyPartDataLabel]
        # Initialising Image Figure on Gridlayout Once at First for Image to be Displayed on
        self.imageFigure = plt.figure()

                                                        # # # # # # # # # # Linking GUI Elements to Methods # # # # # # # # # #

        self.ui.reisizeImageRadiobutton.toggled.connect(self.ResizeImage)
        self.ui.actionOpen_Image.triggered.connect(lambda: self.OpenImage())

                                                        # # # # # # # # # # Initial Show & Hide of UI Elements # # # # # # # # # #

        self.ui.reisizeImageRadiobutton.hide()
        self.ShowAndHideGUISettings("hide", self.generalImageInfoLabels)
        self.ShowAndHideGUISettings("hide", self.dicomSpecificImageInfoLabels)


                                                            # # # # # # # # # # Class Methods Declaration # # # # # # # # # #
  

    # Reading Image Data, and Displaying Image Header Info Accordingly
    def OpenImage(self):

        # Reading Image Try Block, If Carried Out Incorrectly, Error Message Pops Up
        try:
            # Getting File Path, Allowing User to Choose From Only: Bitmap, JPEG or DICOM Files
            self.fileName = QtWidgets.QFileDialog.getOpenFileName(caption="Choose Signal", directory="", filter="Bitmap (*.bmp);; Jpg (*.jpg);; Jpeg (*.jpeg);; Dicom (*.dcm)")[0]
            # If User has Selected a File, Deal Accordingly
            if self.fileName:
                # Checking File Extenstion, If It is a Non-DICOM Image, Read Image Data using OpenCV Library, and If It is a Colored Image, Convert it from BGR Mode to RGB Mode
                # Otherwise, Colored Image won't be Read Correctly. If It is DICOM Image, Read Image Data using PyDICOM Library.
                self.file_extension = os.path.splitext(self.fileName)[1]
                if self.file_extension == '.bmp' or self.file_extension == '.jpg' or self.file_extension == '.jpeg':
                    self.imageData = cv2.imread(self.fileName)
                    if self.GetImageMode() == 'Colored': self.imageData = cv2.cvtColor(self.imageData, cv2.COLOR_BGR2RGB)
                elif self.file_extension == '.dcm':
                    self.dicomDataset = dcmread(self.fileName)
                    self.imageData = self.dicomDataset.pixel_array

                # Displaying Image Try Block, If Carried Out Incorrectly, Error Message Pops Up
                try:
                    # Clearing Image Canvas, and Using 'figimage' Method with False 'resize' Attribute to Display Real Image Size in Canvas without Resizing to Fit Canvas
                    # If Image is DICOM or Uncolored, It is Displayed Using 'gray' Cmap, Otherwise with Colors.
                    self.imageFigure.clear()
                    if self.file_extension == '.dcm' or self.GetImageMode() != 'Colored': self.imageFigure.figimage(self.imageData, resize=False, cmap='gray')
                    else: self.imageFigure.figimage(self.imageData, resize=False)
                    imageCanvas = FigureCanvas(self.imageFigure)
                    self.ui.imageLayout.addWidget(imageCanvas, 0, 0, 1, 1)
                    # If Previous Displayed Image was Resized, So Resize Radiobutton is Checked, To Display Image with Original Size, Radiobutton is Unchecked.
                    if self.ui.reisizeImageRadiobutton.isChecked(): self.ui.reisizeImageRadiobutton.nextCheckState()
                    # Show Image Header Info UI Elements and Showing Resize Radiobutton If Hidden
                    self.ui.reisizeImageRadiobutton.show()
                    self.ShowAndHideGUISettings("show", self.generalImageInfoLabels)
                    # If Image is DICOM, UI Elements Specific to Medical Data in DICOM are Displayed, Else are Hidden
                    if self.file_extension == '.dcm': self.ShowAndHideGUISettings("show", self.dicomSpecificImageInfoLabels)
                    else: self.ShowAndHideGUISettings("hide", self.dicomSpecificImageInfoLabels)
                except: self.ShowErrorMessage("Something Wrong in Displaying Image!      ")

                # Displaying Image Header Information Try Block, If Carried Out Incorrectly, Error Message Pops Up
                try: self.DisplayImageInformation()
                except: self.ShowErrorMessage("Something Wrong in Displaying Image Metadata!      ")

        except: self.ShowErrorMessage("Something Wrong in Opening or Reading Image!      ")


    # Fetching Required Image Information Found in Header
    def DisplayImageInformation(self):

        # If Image is DICOM, General Image Data are Fetched from Header, which are Fetched in Different Way than Non-DICOM Data
        if self.file_extension == '.dcm':
            # Image Size is Brought from Read Pixel Array Size
            self.ui.imageSizeDataLabel.setText(str(self.imageData.shape[0])+' x '+str(self.imageData.shape[1]))
            # Image Size in Bits is Brought from Bit Depth x Image Width x Image Height
            self.ui.imageBitsDataLabel.setText(str(self.dicomDataset.BitsAllocated*self.imageData.shape[0]*self.imageData.shape[1])+' Bits')
            # DICOM Image Bit Depth is Brought from 'Bits Allocated' Element
            self.ui.imageBitDepthDataLabel.setText(str(self.dicomDataset.BitsAllocated)+' Bits/Pixel')
            # DICOM Image is Always Grayscale
            self.ui.imageColorDataLabel.setText('Grayscale')
            # DICOM Specific Medical Image Data in Header are Fetched and If Unfound, 'Undocumented' is Written Instead
            try: self.ui.usedModalityDataLabel.setText(str(self.dicomDataset.Modality))
            except: self.ui.usedModalityDataLabel.setText('Undocumented')
            try: self.ui.patientNameDataLabel.setText(str(self.dicomDataset.PatientName))
            except: self.ui.patientNameDataLabel.setText('Undocumented')
            try: self.ui.patientAgeDataLabel.setText(str(self.dicomDataset.PatientAge))
            except: self.ui.patientAgeDataLabel.setText('Undocumented')
            try: self.ui.bodyPartDataLabel.setText(str(self.dicomDataset.BodyPartExamined))
            except: self.ui.bodyPartDataLabel.setText('Undocumented')
        # If Image is Non-DICOM, Image is Read using Pillow Library, which Gives Image Attributes for Fetching General Image Data from Header,
        else:
            # Image Mode is Mapped to Bit Depth of each Mode (Retrieved From Library Documentation)
            imageMode_to_bitDepth = {'1':1, 'L':8, 'P':8, 'RGB':24, 'RGBA':32, 'CMYK':32, 'YCbCr':24, 'I':32, 'F':32}
            self.imageData = Image.open(self.fileName)
            print(self.imageData.getbands()[0].bits)
            # Image Size is Brought from 'width' and 'height Attributes or Pixel Array Size
            self.ui.imageSizeDataLabel.setText(str(self.imageData.width)+' x '+str(self.imageData.height))
            # Image Size in Bits is Brought from Bit Depth x Image Width x Image Height
            self.ui.imageBitsDataLabel.setText(str(self.imageData.width*self.imageData.height*imageMode_to_bitDepth[self.imageData.mode])+' Bits')
            # Image Bit Depth is Brought from Information of Image Color Mode
            self.ui.imageBitDepthDataLabel.setText(str(imageMode_to_bitDepth[self.imageData.mode])+' Bits/Pixel')
            # Image Color Mode is Brought from 'mode' Attribute
            self.ui.imageColorDataLabel.setText(self.GetImageMode())


    # Resizing Image to Original Size as Displayed or to Fit Canvas Appropriately Using Radiobutton
    def ResizeImage(self):

        # Resizing Image on Canvas Try Block, If Carried Out Incorrectly, Error Message Pops Up
        try:
            # If User Chooses to Resize Image, 'imshow' Method is Used as It Resizes Image to Fit Canvas, while 'resize' Attribute in 'figimage' Resizes Canvas Itself, Not Image
            if self.ui.reisizeImageRadiobutton.isChecked():
                self.imageFigure = plt.figure()
                imageCanvas = FigureCanvas(self.imageFigure)
                self.ui.imageLayout.addWidget(imageCanvas, 0, 0, 1, 1)
                # Adjust Image to Canvas as much as Possible without White Spaces
                plt.axis('off')
                self.imageFigure.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=None, hspace=None)
                # If Image is DICOM or Uncolored, It is Displayed Using 'gray' Cmap
                if self.file_extension == '.dcm' or self.GetImageMode() != 'Colored': plt.imshow(self.imageData, cmap='gray')
                else: plt.imshow(self.imageData)
            # If User Chooses to Revert Image Size to Original, Displaying Using 'figimage' Method and False 'resize' Attribute is Carried Out
            elif not self.ui.reisizeImageRadiobutton.isChecked():
                self.imageFigure.clear()
                # If Image is DICOM or Uncolored, It is Displayed Using 'gray' Cmap
                if self.file_extension == '.dcm' or self.GetImageMode() != 'Colored': self.imageFigure.figimage(self.imageData, resize=False, cmap='gray')
                else: self.imageFigure.figimage(self.imageData, resize=False)
                imageCanvas = FigureCanvas(self.imageFigure)
                self.ui.imageLayout.addWidget(imageCanvas, 0, 0, 1, 1)
        except: self.ShowErrorMessage("Something Wrong in Resizing Image!      ")


                                                                # # # # # # # # # # Helper Functions # # # # # # # # # #


    # Applying Passed Display Method on each of Passed GUI Settings (DICOM Specific or Non-Specific Ones)
    def ShowAndHideGUISettings(self, displayMethod, GUISettings):
        for GUISetting in GUISettings:getattr(GUISetting, displayMethod)()

    # Fetching Image Color Mode from Header
    def GetImageMode(self):
        # Opening Image with 'Pillow' as It has a Mode Attribute
        imageData = Image.open(self.fileName)
        # Returning Color Mode of Image (Binary, Grayscale or Colored) According to Attribute Values (Mapping Retrieved from Documentation)
        if imageData.mode == '1': return 'Binary'
        elif imageData.mode in ['L', 'P', 'I', 'F']: return 'Grayscale'
        elif imageData.mode in ['RGB', 'RGBA', 'CYMK', 'YCbCr', 'HSV']: return 'Colored'

    # Showing an Error Message for Handling Invalid User Actions
    def ShowErrorMessage(self, errorMessage):
        messageBoxElement = QMessageBox()
        messageBoxElement.setWindowTitle("Error!")
        messageBoxElement.setText(errorMessage)
        execute = messageBoxElement.exec_()


                                                                    # # # # # # # # # # Execution  # # # # # # # # # #


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())