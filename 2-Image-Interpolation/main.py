
                                                                    # # # # # # # # # # Imports # # # # # # # # # #


import sys
import cv2
import math
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
        # Initialising Image Figure on Gridlayout Once at First for Image to be Displayed on
        self.imageFigure = plt.figure()
        # Initialising Image Figures to Display Interpolated Images Once at First
        self.nearestNeighbourImageFigure = plt.figure()
        self.bilinearImageFigure = plt.figure()

                                                        # # # # # # # # # # Linking GUI Elements to Methods # # # # # # # # # #

        self.ui.reisizeImageRadiobutton.toggled.connect(self.ResizeImage)
        self.ui.actionOpen_Image.triggered.connect(lambda: self.OpenImage())
        self.ui.zoomingPushButton.clicked.connect(self.ImplementZooming)

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
            fileName = QtWidgets.QFileDialog.getOpenFileName(caption="Choose Signal", directory="", filter="Bitmap (*.bmp);; Jpg (*.jpg);; Jpeg (*.jpeg);; Dicom (*.dcm)")[0]
            # Assign Path of Opened File to Class Variable to Carry Operations on it Only if a File was Chosen
            if fileName: self.fileName = fileName
            # If User has Selected a File, Deal Accordingly
            
            if self.fileName:
                # Checking File Extenstion, If It is a Non-DICOM Image, Read Image Data using OpenCV Library, and If It is a Colored Image, Convert it from BGR Mode to RGB Mode
                # Otherwise, Colored Image won't be Read Correctly. If It is DICOM Image, Read Image Data using PyDICOM Library.
                self.file_extension = os.path.splitext(self.fileName)[1]
                if self.file_extension == '.bmp' or self.file_extension == '.jpg' or self.file_extension == '.jpeg':
                    self.imageData = cv2.imread(self.fileName)
                    if self.GetImageMode() == 'Colored': self.imageData = cv2.cvtColor(self.imageData, cv2.COLOR_BGR2RGB)
                    # Create Grayscale Version of Image if RGB by Reading it as Monochromatic
                    self.imageGrayscaleVersion = cv2.cvtColor(self.imageData, cv2.COLOR_BGR2GRAY)

                elif self.file_extension == '.dcm':
                    self.dicomDataset = dcmread(self.fileName)
                    self.imageData = self.dicomDataset.pixel_array
                    # Since DICOM Images are Inherently Monochromatic, Read Image Data is Directly Assigned to Class Variable Carrying Image Grayscale Version
                    self.imageGrayscaleVersion = self.imageData

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
                    # Clearing Canvases of Scaled Images and Displayed Image Size Before and After Zooming
                    self.ClearInterpolationFigures()
                    # Each Time New Image is Opened, Progress Bar is Returned to Zero Value
                    self.ui.interpolationStatusProgressBar.setValue(0)
                except: self.ShowErrorMessage("Something Wrong in Displaying Image!      ")

                # Displaying Image Header Information Try Block, If Carried Out Incorrectly, Error Message Pops Up
                try: self.DisplayImageInformation()
                except: self.ShowErrorMessage("Something Wrong in Displaying Image Metadata!      ")

        except: self.ShowErrorMessage("Something Wrong in Opening or Reading Image!      ")


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
        # If Image is Non-DICOM, Image is Read using Pillow Library, which Gives Image Attributes for Fetching General Image Data from Header,
        else:
            # Image Mode is Mapped to Bit Depth of each Mode (Retrieved From Library Documentation)
            imageMode_to_bitDepth = {'1':1, 'L':8, 'P':8, 'RGB':24, 'RGBA':32, 'CMYK':32, 'YCbCr':24, 'I':32, 'F':32}
            self.imageData = Image.open(self.fileName)
            self.ui.imageSizeDataLabel.setText(str(self.imageData.width)+' x '+str(self.imageData.height))
            self.ui.imageBitsDataLabel.setText(str(self.imageData.width*self.imageData.height*imageMode_to_bitDepth[self.imageData.mode])+' Bits')
            self.ui.imageBitDepthDataLabel.setText(str(imageMode_to_bitDepth[self.imageData.mode])+' Bits/Pixel')
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


    # Checking Validity of Zooming Operation and Acquiring Its Parameters
    def InitialiseZoomingOpertion(self):

        # Fetching Zooming Factor from User Input SpinBox in GUI
        zoomingFactor = float(self.ui.zoomingFactorSpinBox.text())
        # For Handling Invalid Values of Zooming Factor, Negative Numbers are Not Allowed in GUI Settings
        # As for Zero or Negative Value of Zooming Factor, Zooming Operation is Aborted and an Error Message Appears to User
        if zoomingFactor == 0 or zoomingFactor < 0:
            self.ShowErrorMessage("Zooming Factor Can Neither Be Zero Nor Negative!      ")
            return False, None, None, None, None
        # Dimensions of Scaled Image Pixel Array is Calculated Using Zooming Factor and Dimensions of Original Image Before Scaling
        newNumberOfRows, newNumberofColumns = round(zoomingFactor * self.imageGrayscaleVersion.shape[0]), round(zoomingFactor * self.imageGrayscaleVersion.shape[1])
        # Calculating Progress Step of each Iteration in which Pixel Value of Scaled Image(s) is Calculated, Taking into Consideration Calculation of 
        # Both Nearest Neighbour and Bilinear Interpolated Images. That is Why the 100 Steps of Progress Bar is Divided by Double of New Size of Scaled Image (Calculation of Both Interpolations)
        self.progressStep = 100/(newNumberOfRows * newNumberofColumns * 2)
        # Returning Validity of Zooming Operation (First Boolean) and Its Parameters
        return True, np.zeros((newNumberOfRows, newNumberofColumns)), newNumberOfRows, newNumberofColumns, zoomingFactor


    # Calculating Pixel Values of Scaled Image Using Nearest Neighbour Interpolation
    def InterpolateImageUsingNearestNeighbour(self):

        # Acquiring Interpolation Parameters. If Zooming Operation is Invalid, Abort Operation
        operationStatus, self.nearestNeighbourInterpolatedImage, newNumberOfRows, newNumberofColumns, zoomingFactor = self.InitialiseZoomingOpertion()
        if operationStatus == False: return False
        # Looping on New Scaled Image Pixel Values to Calculate Each Using Nearest Neighbour Interpolation
        for i in range(newNumberOfRows):
            for j in range(newNumberofColumns):
                # Calculating Both Indices of Row and Column of Pixel Value Currently Handled in Scaled Image Mapped in Original Image
                # By Dividing Both Indices by Zooming Factor and Flooring Result If Its Decimal Part is Equal to or Less than 0.5, Otherwise Ceiling
                rowIndexInScaledImage = math.floor(i / zoomingFactor) if math.modf(i / zoomingFactor)[0] <= 0.5 else math.ceil(i / zoomingFactor)
                columnIndexInScaledImage = math.floor(j / zoomingFactor) if math.modf(j / zoomingFactor)[0] <= 0.5 else math.ceil(j / zoomingFactor)
                # Final Mapped Indices in Original Image are Retrieved By Taking Minimum of Previously Calculated Index and Last Possible Index in Original Image
                # Since in Last Pixel Value, the Index Calculated Exceeds Last Possible Index in Original Image, So Calculated Index is Compared with It
                rowIndexInOriginalImage = min( rowIndexInScaledImage,  self.imageGrayscaleVersion.shape[0]-1 )
                columnIndexInOriginalImage = min( columnIndexInScaledImage,  self.imageGrayscaleVersion.shape[1]-1 )
                # Pixel Value Currently Handled in Scaled Image Takes Value of Corresponding Pixel Value of Mapped Indices in Original Image (Its Nearest Neighbour)
                self.nearestNeighbourInterpolatedImage[i, j] = self.imageGrayscaleVersion[rowIndexInOriginalImage, columnIndexInOriginalImage]
                # With Each Iteration, Progress Bar is Incremented and Updated with Current Progress
                self.currentProgress += self.progressStep
                self.ui.interpolationStatusProgressBar.setValue(round(self.currentProgress))
        # Indicate Success of Interpolation Operation
        return True


    # Calculating Pixel Values of Scaled Image Using Bilinear Interpolation
    def InterpolateImageUsingBilinear(self):

        # Acquiring Interpolation Parameters. If Zooming Operation is Invalid, Abort Operation
        operationStatus, self.bilinearInterpolatedImage, newNumberOfRows, newNumberofColumns, zoomingFactor = self.InitialiseZoomingOpertion()
        if operationStatus == False: return False
        # Looping on New Scaled Image Pixel Values to Calculate Each Using Bilinear Interpolation
        for i in range(newNumberOfRows):
            for j in range(newNumberofColumns):
                # Indices of Currently Handled Pixel Mapped in Original Image is Calcualted by Getting Minimum of Indices of Original Image Divided by Zooming Factor
                # and Last Possible Index in Original Image. Reason for Minimum Usage: If Calulated is Greater (Case of Last Pixel(s)), It is Limited by Last Possible Index
                rowIndexInOriginalImage = min( i / zoomingFactor, self.imageGrayscaleVersion.shape[0]-1)
                columnIndexInOriginalImage = min( j / zoomingFactor,  self.imageGrayscaleVersion.shape[1]-1 )
                # If Both Indices of Pixel Value in Scaled Image Mapped in Original Image are Integers, Pixel Value from Original Image is Directly Put in Scaled Image
                if (rowIndexInOriginalImage % 1 == 0) and (columnIndexInOriginalImage % 1 == 0): self.bilinearInterpolatedImage[i, j] = self.imageGrayscaleVersion[round(rowIndexInOriginalImage), round(columnIndexInOriginalImage)]
                # If Row Index of Pixel Value in Scaled Image Mapped in Original Image is Float But Column Index is Integer, Linear Interpolation is Performed Along Mapped Column in Original Image
                # In Calculated Column, Intensities of Both Row Index Floored and Ceiled are Fetched from Original Image, and Each is Multiplied by Its Opposite Distance from Float Row Index Value of Mapped Pixel Currently Calculated
                elif (rowIndexInOriginalImage % 1 != 0) and (columnIndexInOriginalImage % 1 == 0): self.bilinearInterpolatedImage[i, j] = (self.imageGrayscaleVersion[math.floor(rowIndexInOriginalImage), round(columnIndexInOriginalImage)] * (math.ceil(rowIndexInOriginalImage) - rowIndexInOriginalImage)) + (self.imageGrayscaleVersion[math.ceil(rowIndexInOriginalImage), int(columnIndexInOriginalImage)] * (rowIndexInOriginalImage - math.floor(rowIndexInOriginalImage)))
                # If Column Index of Pixel Value in Scaled Image Mapped in Original Image is Float But Row Index is Integer, Linear Interpolation is Performed Along Mapped Row in Original Image
                # In Calculated Row, Intensities of Both Column Index Floored and Ceiled are Fetched from Original Image, and Each is Multiplied by Its Opposite Distance from Float Row Index Value of Mapped Pixel Currently Calculated
                elif (rowIndexInOriginalImage % 1 == 0) and (columnIndexInOriginalImage % 1 != 0): self.bilinearInterpolatedImage[i, j] = (self.imageGrayscaleVersion[round(rowIndexInOriginalImage), math.floor(columnIndexInOriginalImage)] * (math.ceil(columnIndexInOriginalImage) - columnIndexInOriginalImage)) + (self.imageGrayscaleVersion[int(rowIndexInOriginalImage), math.ceil(columnIndexInOriginalImage)] * (columnIndexInOriginalImage - math.floor(columnIndexInOriginalImage)))
                # If Both Indices of Pixel Value in Scaled Image Mapped in Original Image are Floats, Bilinear Interpolation is Performed by Performing Three Operations of Linear Interpolation Using Its Four Nearest Neighbours in Original Image
                elif (rowIndexInOriginalImage % 1 != 0) and (columnIndexInOriginalImage % 1 != 0):
                    # Linear Interpolation is Performed Along First Row by Flooring Row Index, Fetching the First Two Neighbours of that Row by Flooring and Ceiling Column Value and Calculating Value of Pixel above Currently Handled Pixel in First Row
                    firstRowIntermediateIntensity = ( self.imageGrayscaleVersion[math.floor(rowIndexInOriginalImage), math.floor(columnIndexInOriginalImage)] * (math.ceil(columnIndexInOriginalImage) - columnIndexInOriginalImage) ) + ( self.imageGrayscaleVersion[math.floor(rowIndexInOriginalImage), math.ceil(columnIndexInOriginalImage)] * (columnIndexInOriginalImage - math.floor(columnIndexInOriginalImage)) )
                    # Linear Interpolation is Performed Along Second Row by Ceiling Row Index, Fetching the Second Two Neighbours of that Row by Flooring and Ceiling Column Value and Calculating Value of Pixel below Currently Handled Pixel in Second Row
                    secondRowIntermediateIntensity = ( self.imageGrayscaleVersion[math.ceil(rowIndexInOriginalImage), math.floor(columnIndexInOriginalImage)] * (math.ceil(columnIndexInOriginalImage) - columnIndexInOriginalImage) ) + ( self.imageGrayscaleVersion[math.ceil(rowIndexInOriginalImage), math.ceil(columnIndexInOriginalImage)] * (columnIndexInOriginalImage - math.floor(columnIndexInOriginalImage)) )
                    # Linear Interpolation is Performed Using Intermediate Intensity Values Previously Calculated Along Column Combining Locations of Both Pixel and that Currently Handled
                    self.bilinearInterpolatedImage[i, j] = (firstRowIntermediateIntensity * (math.ceil(rowIndexInOriginalImage) - rowIndexInOriginalImage)) + (secondRowIntermediateIntensity * (rowIndexInOriginalImage - math.floor(rowIndexInOriginalImage)))
                # With Each Iteration, Progress Bar is Incremented and Updated with Current Progress
                self.currentProgress += self.progressStep
                self.ui.interpolationStatusProgressBar.setValue(round(self.currentProgress))
        # Indicate Success of Interpolation Operation
        return True


    # Carrying out Zooming Operation from Initialisation to Calculation and Display
    def ImplementZooming(self):

        # Implementation of Zooming Operation Try Block, If Carried Out Incorrectly, Error Message Pops Up
        try:
            # Initialising Progress of Zooming Operation with Zero
            self.currentProgress = 0
            # Clearing Canvases of Scaled Images and Displayed Image Size Before and After Zooming
            self.ClearInterpolationFigures()
            # Applying Nearest Neighbour Interpolation. If Operation Failed due to Invalidity, Abort
            if self.InterpolateImageUsingNearestNeighbour() == False: return
            # Displaying Nearest Neighbour Interpolated Image on Corresponding Canvas
            self.nearestNeighbourImageFigure.figimage(self.nearestNeighbourInterpolatedImage, resize=False, cmap='gray')
            nearestNeighbourImageCanvas = FigureCanvas(self.nearestNeighbourImageFigure)
            self.ui.nearestNeighbourInterpolatedImageGridLayout.addWidget(nearestNeighbourImageCanvas, 0, 0, 1, 1)
            # Applying Bilinear Interpolation. If Operation Failed due to Invalidity, Abort
            if self.InterpolateImageUsingBilinear() == False: return
            # Displaying Bilinear Interpolated Image on Corresponding Canvas
            self.bilinearImageFigure.figimage(self.bilinearInterpolatedImage, resize=False, cmap='gray')
            bilinearImageCanvas = FigureCanvas(self.bilinearImageFigure)
            self.ui.bilinearInterpolatedImageGridLayout.addWidget(bilinearImageCanvas, 0, 0, 1, 1)
            # Displaying Image Size Before and After Zooming on GUI
            self.ui.originalImageSizeDataLabel.setText(str(self.imageGrayscaleVersion.shape[0])+' Rows x '+str(self.imageGrayscaleVersion.shape[1])+' Columns')
            self.ui.imageSizeAfterZoomingDataLabel.setText(str(self.bilinearInterpolatedImage.shape[0])+' Rows x '+str(self.bilinearInterpolatedImage.shape[1])+' Columns')
        except: self.ShowErrorMessage("Something Wrong in Zooming Operation!      ")


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


    # Refreshing Canvases of Interpolated Images for Repeated Display
    def ClearInterpolationFigures(self):
        # Clear Nearest Neighbour Interpolated Image Canvas
        self.nearestNeighbourImageFigure.clear()
        self.nearestNeighbourImageFigure.canvas.draw()
        # Clear Bilinear Interpolated Image Canvas
        self.bilinearImageFigure.clear()
        self.bilinearImageFigure.canvas.draw()
        # Clearing Displayed Image Size Before and After Zooming on GUI
        self.ui.originalImageSizeDataLabel.setText('')
        self.ui.imageSizeAfterZoomingDataLabel.setText('')


                                                                    # # # # # # # # # # Execution  # # # # # # # # # #


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())