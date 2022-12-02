
                                                                    # # # # # # # # # # Imports # # # # # # # # # #

import sys
import cv2
import os.path
import numpy as np
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

        # Initialising Image Figure on Gridlayout Once at First for Image to be Displayed on (Tab 1)
        self.imageFigure = plt.figure()
        # Initialising Figures of Images and Histogram Before and After Equalisation on Gridlayout Once at First for Image to be Displayed on
        self.originalImageFigure = plt.figure()
        self.originalHistogramFigure = plt.figure()
        self.equalisedImageFigure = plt.figure()
        self.equalisedHistogramFigure = plt.figure()


                                                        # # # # # # # # # # Linking GUI Elements to Methods # # # # # # # # # #


        self.ui.reisizeImageRadiobutton.toggled.connect(self.ResizeImage)
        self.ui.actionOpen_Image.triggered.connect(lambda: self.OpenImage())


                                                        # # # # # # # # # # Initial Show & Hide of UI Elements # # # # # # # # # #


        self.ui.reisizeImageRadiobutton.hide()
        self.ShowAndHideGUISettings("hide", self.generalImageInfoLabels)
        self.ShowAndHideGUISettings("hide", self.dicomSpecificImageInfoLabels)


                                                            # # # # # # # # # # Class Methods Declaration # # # # # # # # # #


                                                            # # # # # # # Using Tab 1 & Tab 2 Functionalities # # # # # # # #
                                                                    

    # Reading Image Data, and Displaying Image Header Info Accordingly
    def OpenImage(self):

        # Reading Image Try Block, If Carried Out Incorrectly, Error Message Pops Up
        try:
            # Getting File Path, Allowing User to Choose From Only: Bitmap, JPEG or DICOM Files
            self.fileName = QtWidgets.QFileDialog.getOpenFileName(caption="Choose Signal", directory="", filter="Tif (*.tif);; Bitmap (*.bmp);; Jpg (*.jpg);; Dicom (*.dcm)")[0]
            # If User has Selected a File, Deal Accordingly
            if self.fileName:
                # Checking File Extenstion, If It is a Non-DICOM Image, Read Image Data using OpenCV Library, and If It is a Colored Image, Convert it from BGR Mode to RGB Mode
                # Otherwise, Colored Image won't be Read Correctly. If It is DICOM Image, Read Image Data using PyDICOM Library.
                self.file_extension = os.path.splitext(self.fileName)[1]
                if self.file_extension != '.dcm':
                    self.imageData = cv2.imread(self.fileName, -1)
                    if self.GetImageMode() == 'Colored': self.imageData = cv2.cvtColor(self.imageData, cv2.COLOR_BGR2RGB)
                elif self.file_extension == '.dcm':
                    self.dicomDataset = dcmread(self.fileName)
                    self.imageData = self.dicomDataset.pixel_array

            # Displaying Image Try Block, If Carried Out Incorrectly, Error Message Pops Up
                try:
                    # Clearing Image Canvas,
                    self.imageFigure.clear()
                    self.imageFigure.canvas.draw()

                    # Displaying Image Header Information Try Block, If Carried Out Incorrectly, Error Message Pops Up
                    try: self.DisplayImageInformation()
                    except: self.ShowErrorMessage("Something Wrong in Displaying Image Metadata!      ")

                    # Using 'figimage' Method with False 'resize' Attribute to Display Real Image Size in Canvas without Resizing to Fit Canvas
                    # If Image is DICOM or Uncolored, It is Displayed Using 'gray' Cmap, Otherwise with Colors.
                    if self.file_extension == '.dcm' or self.GetImageMode() != 'Colored': self.imageFigure.figimage(self.imageData, resize=False, cmap='gray', vmin=0, vmax=2**(self.imageBitDepth)-1)
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

                try:
                    # TAB 2 Sequence:
                    # When Chosen Image is Displayed in Tab 1, Its Equivalent Grayscale Version is Displayed in Tab 2, Along with Corresponding Histogram of Grayscale Version
                    # Then, Grayscale Image Version is Equalised and Displayed, Along with Its Corresponding Histogram
                    self.DisplayGrayScaleVersion()
                    self.ConstructHistogram(self.grayScaleVersion, self.originalHistogramFigure, self.ui.originalHistogramGridLayout)
                    self.DisplayEqualisedGrayScaleVersion()
                    self.ConstructHistogram(self.equalisedGrayScaleImage, self.equalisedHistogramFigure, self.ui.equalisedHistogramGridLayout)
                except: self.ShowErrorMessage("Something Wrong in Equalising Image Histogram!      ")

        except: self.ShowErrorMessage("Something Wrong in Opening or Reading Image!      ")


                                                            # # # # # # # # # # Tab 2 Functionalities # # # # # # # # # # #


    # Calculate and Show Grayscale Version of Image in Tab 2 of GUI
    def DisplayGrayScaleVersion(self):

        # Constructing Grayscale Version of Image with Same Size as Original Image
        self.grayScaleVersion = np.zeros((self.imageData.shape[0], self.imageData.shape[1]))
        # If Image is RGB, Transform it into Grayscale
        if len(self.imageData.shape) == 3: self.grayScaleVersion = np.round((0.2989 * self.imageData[:, :, 0]) + (0.5870 * self.imageData[:, :, 1]) + (0.1140 * self.imageData[:, :, 2])).astype('int')
        # If Image is Already Grayscale, Assign it as It is
        elif len(self.imageData.shape) == 2: self.grayScaleVersion = self.imageData

        # Clearing Old Image and Displaying New One on Figure
        self.originalImageFigure.clear()
        self.originalImageFigure.canvas.draw()
        self.originalImageFigure.figimage(self.grayScaleVersion, resize=False, cmap='gray', vmin=0, vmax=2**(self.imageBitDepth)-1)
        originalImageCanvas = FigureCanvas(self.originalImageFigure)
        self.ui.originalImageGridLayout.addWidget(originalImageCanvas, 0, 0, 1, 1)


    # Calculate Histogram of Passed Image (Unequalised or Equalised) and Show It Beside Image in GUI
    def ConstructHistogram(self, imageToDrawHistogramFor, histogramFigure, histogramGridLayout):

        # Construct an Array of All Graylevel Intensities that can be Available in Iamge using Bit Depth 
        grayLevelIntensities = np.arange(0, 2**(self.imageBitDepth), 1)
        # Construct an Empty Array to Fill Using Count of Grayscale Occurrences
        grayLevelFrequencies = np.zeros((2**(self.imageBitDepth)))

        # Looping on Each Pixel Intensity Value in Image Array and Incrementing Corresponding Intensity in Array of Intensity Occurrences Count
        for i in range(imageToDrawHistogramFor.shape[0]):
            for j in range(imageToDrawHistogramFor.shape[1]):
                grayLevelFrequencies[int(imageToDrawHistogramFor[i, j])] += 1
        # Normalising Count of Intensity Occurrences Using Image Size
        self.normalisedGrayLevelFrequencies = grayLevelFrequencies / int(imageToDrawHistogramFor.shape[0] * imageToDrawHistogramFor.shape[1])

        # Clearing Old Histogram and Displaying New One on Figure
        histogramFigure.clear()
        histogramFigure.canvas.draw()
        axes = histogramFigure.add_subplot()
        axes.bar(grayLevelIntensities, self.normalisedGrayLevelFrequencies)
        histogramCanvas = FigureCanvas(histogramFigure)
        histogramGridLayout.addWidget(histogramCanvas, 0, 0, 1, 1)


    def DisplayEqualisedGrayScaleVersion(self):

        # Construct an Empty Array to Fill with Cumulative Probability of Each Pixel Intensity
        cumulativeNormalisedGrayLevelFrequencies = np.zeros((2**(self.imageBitDepth)))
        # Construct an Empty Array to Fill with New Values of Graylevel Intensities After Equalisation
        equalisedGrayLevelIntensities = np.zeros((2**(self.imageBitDepth)))

        # Computing Cumulative Probability of Each Pixel Intensity by Summing Probabilities of All Intensities Up to It
        for i in range(cumulativeNormalisedGrayLevelFrequencies.shape[0]):
            cumulativeNormalisedGrayLevelFrequencies[i] = np.sum(self.normalisedGrayLevelFrequencies[0:i+1])
        # Calculating Corresponding Value of Each Graylevel Intensity After Equalisation by Multiplying Number of Graylevels Present in Image with Its Cumulative Probabilty
            equalisedGrayLevelIntensities[i] = round((2**(self.imageBitDepth)-1) * cumulativeNormalisedGrayLevelFrequencies[i])

        # Construct an Eempty 2D Array to Fill with New Image After Equalisation
        self.equalisedGrayScaleImage = np.zeros((self.grayScaleVersion.shape[0], self.grayScaleVersion.shape[1]))
        # Looping on Each Pixel Intensity Value in Image Before Equalisation, and Replacing it with Its Equivalent Value After Equalisation
        for i in range(self.grayScaleVersion.shape[0]):
            for j in range(self.grayScaleVersion.shape[1]):
                self.equalisedGrayScaleImage[i, j] = equalisedGrayLevelIntensities[self.grayScaleVersion[i, j]]

        # Clearing Old Equalised Image and Displaying New One on Figure
        self.equalisedImageFigure.clear()
        self.equalisedImageFigure.canvas.draw()
        self.equalisedImageFigure.figimage(self.equalisedGrayScaleImage, resize=False, cmap='gray', vmin=0, vmax=2**(self.imageBitDepth)-1)
        equalisedImageCanvas = FigureCanvas(self.equalisedImageFigure)
        self.ui.equalisedImageGridLayout.addWidget(equalisedImageCanvas, 0, 0, 1, 1)


                                                            # # # # # # # # # # Tab 1 Functionalities # # # # # # # # # # #


    # Fetching Required Image Information Found in Header
    def DisplayImageInformation(self):

        # If Image is DICOM, General Image Data are Fetched from Header, which are Fetched in Different Way than Non-DICOM Data
        if self.file_extension == '.dcm':
            
            self.ui.imageSizeDataLabel.setText(str(self.imageData.shape[0])+' x '+str(self.imageData.shape[1]))
            self.ui.imageBitsDataLabel.setText(str(self.dicomDataset.BitsAllocated*self.imageData.shape[0]*self.imageData.shape[1])+' Bits')
            self.ui.imageBitDepthDataLabel.setText(str(self.dicomDataset.BitsAllocated)+' Bits/Pixel')
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
            # Assigning Image Bit Depth as Class Attribute
            self.imageBitDepth = self.dicomDataset.BitsStored
        
        # If Image is Non-DICOM, Image is Read using Pillow Library, which Gives Image Attributes for Fetching General Image Data from Header,
        else:
            # Image Mode is Mapped to Bit Depth of each Mode Using Pixel Value Data Type
            imageType_to_bitDepth = {np.dtype('bool'):8, np.dtype('uint8'):8, np.dtype('int8'):8, np.dtype('uint16'):16, np.dtype('int16'):16, np.dtype('uint32'):32, np.dtype('int32'):32, np.dtype('float32'):32, np.dtype('float64'):64}
            pillowImageData = Image.open(self.fileName)
            self.ui.imageSizeDataLabel.setText(str(pillowImageData.width)+' x '+str(pillowImageData.height))
            self.ui.imageBitsDataLabel.setText(str(pillowImageData.width*pillowImageData.height*imageType_to_bitDepth[np.asarray(self.imageData).dtype])+' Bits')
            self.ui.imageBitDepthDataLabel.setText(str(imageType_to_bitDepth[np.asarray(pillowImageData).dtype] * len(pillowImageData.getbands()))+' Bits/Pixel')
            self.ui.imageColorDataLabel.setText(self.GetImageMode())
            # Assigning Image Bit Depth as Class Attribute
            self.imageBitDepth = imageType_to_bitDepth[np.asarray(pillowImageData).dtype]


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
                if self.file_extension == '.dcm' or self.GetImageMode() != 'Colored': plt.imshow(self.imageData, cmap='gray', vmin=0, vmax=2**(self.imageBitDepth)-1)
                else: plt.imshow(self.imageData)
            
            # If User Chooses to Revert Image Size to Original, Displaying Using 'figimage' Method and False 'resize' Attribute is Carried Out
            elif not self.ui.reisizeImageRadiobutton.isChecked():
                self.imageFigure.clear()
                # If Image is DICOM or Uncolored, It is Displayed Using 'gray' Cmap
                if self.file_extension == '.dcm' or self.GetImageMode() != 'Colored': self.imageFigure.figimage(self.imageData, resize=False, cmap='gray', vmin=0, vmax=2**(self.imageBitDepth)-1)
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