
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
from skimage.data import shepp_logan_phantom
from skimage.transform import radon, iradon, rescale
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
        # Initialising Image Figures on Gridlayout Once at First for Image to be Displayed on (Tab 2)
        self.originalPhantomFigure = plt.figure()
        self.phantomSinogramFigure = plt.figure()
        self.unfilteredLaminogramStep20Figure = plt.figure()
        self.unfilteredLaminogramStep1Figure = plt.figure()
        self.ramLakLaminogramStep1Figure = plt.figure()
        self.hammingLaminogramStep1Figure = plt.figure()


                                                        # # # # # # # # # # Linking GUI Elements to Methods # # # # # # # # # #


        self.ui.reisizeImageRadiobutton.toggled.connect(self.ResizeImage)
        self.ui.actionOpen_Image.triggered.connect(lambda: self.OpenImage())


                                                        # # # # # # # # # # Initial Call of Class Functions # # # # # # # # # #


        self.ui.reisizeImageRadiobutton.hide()
        self.ShowAndHideGUISettings("hide", self.generalImageInfoLabels)
        self.ShowAndHideGUISettings("hide", self.dicomSpecificImageInfoLabels)
        # TAB 2 Functions
        self.ConstructPhantomAndSinogram()
        self.ConstructLaminograms()


                                                            # # # # # # # # # # Class Methods Declaration # # # # # # # # # #


                                                            # # # # # # # # # # Using Tab 1 Functionalities # # # # # # # # #
                                                                    

    # Reading Image Data, and Displaying Image Header Info Accordingly
    def OpenImage(self):

        # Reading Image Try Block, If Carried Out Incorrectly, Error Message Pops Up
        try:
            # Getting File Path, Allowing User to Choose From Only: Bitmap, JPEG or DICOM Files
            self.fileName = QtWidgets.QFileDialog.getOpenFileName(caption="Choose Signal", directory="", filter="Jpg (*.jpg);; Tif (*.tif);; Bitmap (*.bmp);; Dicom (*.dcm)")[0]
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
        except: self.ShowErrorMessage("Something Wrong in Opening or Reading Image!      ")


                                                            # # # # # # # # # # Tab 2 Functionalities # # # # # # # # # # #


    # Fetch and Display Shepp-Logan Phantom and Its Sinogram
    def ConstructPhantomAndSinogram(self):

        # Fetching Shepp-Logan phantom from library and rescaling its size to 256x256 (initially 400x400)
        self.phantom = shepp_logan_phantom(); self.phantom = rescale(self.phantom, scale=0.64, mode='reflect')
        # Forming theta values whose count is the same as image size to construct the sinogram
        # Sinogram: stacking of 1D projections (radon transforms) of image obtained at different angles (theta)
        thetas = np.linspace(0., 180., 256, endpoint=False)
        sinogram = radon(self.phantom, theta=thetas); sinogram = np.transpose(sinogram)
        # Displaying phantom and its sinogram
        self.DisplayFigure(self.originalPhantomFigure, None, self.ui.originalPhantomGridLayout, self.phantom)
        self.DisplayFigure(self.phantomSinogramFigure, ['ϱ', 'θ'], self.ui.phantomSinogramGridLayout, sinogram)


    # Calculate and Display Different Laminogram Examples
    def ConstructLaminograms(self):

        # Forming theta values with steps 20 and 1 degree(s) for cosntruction of required laminogram
        step20Thetas, step1Thetas = np.arange(0, 180, 20), np.arange(0, 180, 1)
        # Constructing each laminogram by taking the inverse radon transform of the sinogram formed at the specified angles,
        # with type of filter applied on those projections specified, if any
        # Laminogram: Sum of back-projected images formed from the radon transforms taken at different angles of the image
        unfilteredLaminogramStep20 = iradon(radon(self.phantom, theta=step20Thetas), theta=step20Thetas, filter_name=None)
        unfilteredLaminogramStep1 = iradon(radon(self.phantom, theta=step1Thetas), theta=step1Thetas, filter_name=None)
        ramLakLaminogramStep1 = iradon(radon(self.phantom, theta=step1Thetas), theta=step1Thetas, filter_name='ramp')
        hammingLaminogramStep1 = iradon(radon(self.phantom, theta=step1Thetas), theta=step1Thetas, filter_name='hamming')
        # Displaying required laminograms
        self.DisplayFigure(self.unfilteredLaminogramStep20Figure, None, self.ui.unfilteredLaminogramStep20GridLayout, unfilteredLaminogramStep20)
        self.DisplayFigure(self.unfilteredLaminogramStep1Figure, None, self.ui.unfilteredLaminogramStep1GridLayout, unfilteredLaminogramStep1)
        self.DisplayFigure(self.ramLakLaminogramStep1Figure, None, self.ui.ramLakLaminogramStep1GridLayout, ramLakLaminogramStep1)
        self.DisplayFigure(self.hammingLaminogramStep1Figure, None, self.ui.hammingLaminogramStep1GridLayout, hammingLaminogramStep1)

        # Observations:
        # - The more projections at different angles are taken, the closer the laminogram estimate of the phantom is to the real image of the phantom
        #   However, the image is blurred.
        # - Both Ram-Lak and Hamming filters remove the blurring but the Ram-Lak creates a bit of ringing to the sharpness of its function, which is solved by using
        #   the hamming filter, a smoother function, that creates less ringer but a more blurred image than Ram-Lak because its central lobe has a higher width.
        

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


    # Display Passed Image in Its Passed Place with Specified Parameters
    def DisplayFigure(self, figure, axesTitles, gridLayout, imageToDisplay):
        # Create the subplot of the figure with its settings varing between axes titles and ticks
        axes = figure.add_subplot()
        if axesTitles:
            axes.xaxis.set_label_text(axesTitles[0]); axes.yaxis.set_label_text(axesTitles[1])
        axes.xaxis.set_ticks_position('top'); axes.xaxis.set_ticks(np.arange(0, 255, 50)); axes.yaxis.set_ticks(np.arange(0, 255, 50))
        # Displaying image on its specific place in the GUI
        figureCanvas = FigureCanvas(figure); gridLayout.addWidget(figureCanvas, 0, 0, 1, 1)
        axes.imshow(imageToDisplay, cmap="gray", origin='upper')

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