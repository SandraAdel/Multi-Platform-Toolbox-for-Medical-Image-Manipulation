
                                                                    # # # # # # # # # # Imports # # # # # # # # # #

import sys
import cv2
import copy
import random
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
        # Initialising Figures of Images (Original, Enhanced, Noisy & Denoised ) on Gridlayout Once at First for Images to be Displayed on (Tabs 2 & 3)
        self.originalImageFigure = plt.figure()
        self.enhancedImageFigure = plt.figure()
        self.noisyImageFigure = plt.figure()
        self.denoisedImageFigure = plt.figure()


                                                        # # # # # # # # # # Linking GUI Elements to Methods # # # # # # # # # #


        self.ui.reisizeImageRadiobutton.toggled.connect(self.ResizeImage)
        self.ui.actionOpen_Image.triggered.connect(lambda: self.OpenImage())
        self.ui.unsharpMaskingPushButton.clicked.connect(self.EnhanceImage)
        self.ui.applyNoisePushButton.clicked.connect(self.AddImpulseNoise)
        self.ui.medianFilteringPushButton.clicked.connect(self.DenoiseImage)


                                                        # # # # # # # # # # Initial Show & Hide of UI Elements # # # # # # # # # #


        self.ui.reisizeImageRadiobutton.hide()
        self.ShowAndHideGUISettings("hide", self.generalImageInfoLabels)
        self.ShowAndHideGUISettings("hide", self.dicomSpecificImageInfoLabels)


                                                            # # # # # # # # # # Class Methods Declaration # # # # # # # # # #


                                                        # # # # # # # Using Tab 1, Tab 2 & Tab 3 Functionalities # # # # # # # #
                                                                    

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

                # TAB 2 and 3
                # Clearing tab 2 and tab 3 figures each time a new image is opened to delete the data of the old image
                self.enhancedImageFigure.clear()
                self.enhancedImageFigure.canvas.draw()
                self.noisyImageFigure.clear()
                self.noisyImageFigure.canvas.draw()
                self.denoisedImageFigure.clear()
                self.denoisedImageFigure.canvas.draw()
                # Disabling user to apply median filter on image in tab 3 unless he/she applied noise on it first
                self.ui.medianFilteringKernelSizeSpinbox.setEnabled(False)
                self.ui.medianFilteringPushButton.setEnabled(False)
                # Displaying grayscale version of image in tab 2 to apply unsharp masking on it
                self.DisplayGrayScaleVersion()

        except: self.ShowErrorMessage("Something Wrong in Opening or Reading Image!      ")


                                                            # # # # # # # # # # Tab 2 Functionalities # # # # # # # # # # #


    # Calculate and Show Grayscale Version of Image in Tab 2 (Unsharp Masking) of GUI
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

        
    # Calculating Enhanced Image Result Using Unsharp Masking
    def EnhanceImage(self):

        # If user input of kernel size is invalid, output an error message and do not perform filtering
        if (int(self.ui.unsharpMaskingKernelSizeSpinbox.text()) <= 0) or (int(self.ui.unsharpMaskingKernelSizeSpinbox.text()) == 1) or (int(self.ui.unsharpMaskingKernelSizeSpinbox.text()) % 2 == 0):
            self.ShowErrorMessage("Invalid Kernel Size!      ")
            return
        
        # If user input of K value is invalid, output an error message and do not perform filtering
        if float(self.ui.unsharpMaskingKValueSpinbox.text()) < 0:
            self.ShowErrorMessage("Invalid K Value!      ")
            return

        # Clear figure where enhanced image is displayed between each filtering process performed
        self.enhancedImageFigure.clear()
        self.enhancedImageFigure.canvas.draw()

        # Initialise an empty array with same shape of original image to store output of low pass filter in, resulting in a blurred image
        blurredImage = np.zeros((self.grayScaleVersion.shape[0], self.grayScaleVersion.shape[1]))

        # Image Padding:
        # Create an empty array of size equals that of the original image in addition to the padding, which is equal to kernel size - 1 for both the rows and columns
        # (m-1)/2 extra row at top and bottom of image, and (n-1)/2 extra column at beginning and end of image
        # and placing the image values in the middle of the padded image
        kernelSize = int(self.ui.unsharpMaskingKernelSizeSpinbox.text())
        paddedImage = np.zeros((self.grayScaleVersion.shape[0]+(kernelSize-1), self.grayScaleVersion.shape[1]+(kernelSize-1)))
        paddedImage[int((kernelSize-1)/2):-int((kernelSize-1)/2), int((kernelSize-1)/2):-int((kernelSize-1)/2)] = self.grayScaleVersion

        # Looping on original image values in padded image (kernel center point at image values leaving aside padded values)
        for i in range(int((kernelSize-1)/2), paddedImage.shape[0] - int((kernelSize-1)/2)):
            for j in range(int((kernelSize-1)/2), paddedImage.shape[1] - int((kernelSize-1)/2)):

                # Slicing the neighbourhood of the targetted pixel at hand according to kernel size
                slicedNeighbourhood = paddedImage[i-int((kernelSize-1)/2):i+int((kernelSize-1)/2)+1, j-int((kernelSize-1)/2):j+int((kernelSize-1)/2)+1]

                # Summing all values of neighbourhood, and placing result divided by number of pixels in the box kernel
                # in the location of the targetted pixel at hand in the resulted blurred image array (which is not padded)
                neighbourhoodSum = 0
                for element in np.nditer(slicedNeighbourhood):
                    neighbourhoodSum += element

                blurredImage[i-int((kernelSize-1)/2), j-int((kernelSize-1)/2)] = neighbourhoodSum/(kernelSize**2)

        # Obtaining user input of K value, calculating the unsharp mask of the image by subtracting the resulted blurred image from the original image, and multiplying result by K value
        kValue = float(self.ui.unsharpMaskingKValueSpinbox.text())
        unsharpMask = (self.grayScaleVersion - blurredImage) * kValue
        # Obtaining enhanced image by adding the calculated unsharp mask to the original grayscale image
        enhancedImage = self.grayScaleVersion + unsharpMask

        # Rescaling image values if it is out of the dynamic range of the original image according to its bit depth
        # by subtracting the minimum value of the image from each value in it, so that its minimum reaches zero and dividing by its range, to normalise it between 0-1
        # then multiplying the result by the new intended maximum grayscale level, which is (2 to power of bit depth - 1)
        if (np.min(enhancedImage) < 0) or (np.max(enhancedImage) > 2**(self.imageBitDepth) - 1):
            enhancedImage = np.round( ((enhancedImage - np.min(enhancedImage)) / (np.max(enhancedImage) - np.min(enhancedImage))) * (2**(self.imageBitDepth)-1) )

        # Clearing Old Image and Displaying New One on Figure
        self.enhancedImageFigure.figimage(enhancedImage, resize=False, cmap='gray', vmin=0, vmax=2**(self.imageBitDepth)-1)
        enhancedImageCanvas = FigureCanvas(self.enhancedImageFigure)
        self.ui.enhancedImageGridLayout.addWidget(enhancedImageCanvas, 0, 0, 1, 1)

        
                                                            # # # # # # # # # # Tab 3 Functionalities # # # # # # # # # # #

        
    # Noisying Image Through Salt and Pepper Noise
    def AddImpulseNoise(self):

        # If user input of noise ratio is invalid, output an error message and do not add noise to the image
        if (float(self.ui.noiseRatioSpinBox.text()) < 0) or (float(self.ui.noiseRatioSpinBox.text()) > 1):
            self.ShowErrorMessage("Invalid Noise Ratio!      ")
            return
        
        # If user input of noise ratio of zero value, which means no noise which is not the target of the application, output an error message
        if float(self.ui.noiseRatioSpinBox.text()) == 0:
            self.ShowErrorMessage("Please Enter a Noise Ratio!      ")
            return
        
        # Clear figure where noisy image is displayed between each noising process performed
        self.noisyImageFigure.clear()
        self.noisyImageFigure.canvas.draw()

        # Take a copy of the original image to corrupt it by adding noise, and obtain user input noise ratio
        self.noisyImage = np.copy(self.grayScaleVersion)
        amountOfNoiseInImage = float(self.ui.noiseRatioSpinBox.text())

        # Randomising ratio of salt dots to pepper dots in image as a percentage of total number of corrupted pixels in image
        saltNoiseRatio = random.random()

        # Salt:
        # Calculating number of salt values in image by multiplying the ratio of corruption in image inputted by the user by the number of pixels in the image
        # to get total number of corrupted pixels, and muliplying result by the randomised value of salt ratio of the total number of corrupted pixels
        numberOfSalt = np.round(amountOfNoiseInImage * self.noisyImage.shape[0]*self.noisyImage.shape[1] * saltNoiseRatio)
        # For each salt dot to be added, its row and column indices are randomly found, and the pixel value is placed by highest grayscale value in the dynamic range of image
        for i in range(int(numberOfSalt)):
            pixelRowIndex, pixelColumnIndex = random.randint(0, self.noisyImage.shape[0]-1), random.randint(0, self.noisyImage.shape[1]-1)
            self.noisyImage[pixelRowIndex, pixelColumnIndex] = 2**(self.imageBitDepth) - 1

        # Pepper:
        # Calculating number of pepper values in image by multiplying the ratio of corruption in image inputted by the user by the number of pixels in the image
        # to get total number of corrupted pixels, and muliplying result by the randomised value of salt ratio of the total number of corrupted pixels subtracted from 1
        # to get pepper ratio out of the total number of corrupted pixels
        numberOfPepper = np.round(amountOfNoiseInImage * self.noisyImage.shape[0]*self.noisyImage.shape[1] * (1-saltNoiseRatio))
        # For each pepper dot to be added, its row and column indices are randomly found, and the pixel value is placed by lowest grayscale value in the dynamic range of image, which is zero
        for i in range(int(numberOfPepper)):
            pixelRowIndex, pixelColumnIndex = random.randint(0, self.noisyImage.shape[0]-1), random.randint(0, self.noisyImage.shape[1]-1)
            self.noisyImage[pixelRowIndex, pixelColumnIndex] = 0

        # Clearing Old Image and Displaying New One on Figure
        self.noisyImageFigure.figimage(self.noisyImage, resize=False, cmap='gray', vmin=0, vmax=2**(self.imageBitDepth)-1)
        noisyImageCanvas = FigureCanvas(self.noisyImageFigure)
        self.ui.noisyImageGridLayout.addWidget(noisyImageCanvas, 0, 0, 1, 1)

        # Enabling user to perform the filtering process since they added noise to the image
        self.ui.medianFilteringKernelSizeSpinbox.setEnabled(True)
        self.ui.medianFilteringPushButton.setEnabled(True)


    # Applying Median Filter on Noised Image to Remove Salt and Pepper Noise
    def DenoiseImage(self):

        # If user input of noise ratio is invalid, output an error message and do not add noise to the image
        if (int(self.ui.medianFilteringKernelSizeSpinbox.text()) <= 0) or (int(self.ui.medianFilteringKernelSizeSpinbox.text()) == 1) or (int(self.ui.medianFilteringKernelSizeSpinbox.text()) % 2 == 0):
            self.ShowErrorMessage("Invalid Kernel Size!      ")
            return

        # Clear figure where denoised image is displayed between each denoising process performed
        self.denoisedImageFigure.clear()
        self.denoisedImageFigure.canvas.draw()

        # Initialise an empty array with same shape of original image to store output of median filter in, resulting in a denoised image
        denoisedImage = np.zeros((self.noisyImage.shape[0], self.noisyImage.shape[1]))

        # Image Padding:
        # Create an empty array of size equals that of the original image in addition to the padding, which is equal to kernel size - 1 for both the rows and columns
        # (m-1)/2 extra row at top and bottom of image, and (n-1)/2 extra column at beginning and end of image
        # and placing the image values in the middle of the padded image
        kernelSize = int(self.ui.medianFilteringKernelSizeSpinbox.text())
        paddedImage = np.zeros((self.noisyImage.shape[0]+(kernelSize-1), self.noisyImage.shape[1]+(kernelSize-1)))
        paddedImage[int((kernelSize-1)/2):-int((kernelSize-1)/2), int((kernelSize-1)/2):-int((kernelSize-1)/2)] = self.noisyImage

        # Looping on original image values in padded image (kernel center point at image values leaving aside padded values)
        for i in range(int((kernelSize-1)/2), paddedImage.shape[0] - int((kernelSize-1)/2)):
            for j in range(int((kernelSize-1)/2), paddedImage.shape[1] - int((kernelSize-1)/2)):

                # Slicing the neighbourhood of the targetted pixel at hand according to kernel size
                slicedNeighbourhood = paddedImage[i-int((kernelSize-1)/2):i+int((kernelSize-1)/2)+1, j-int((kernelSize-1)/2):j+int((kernelSize-1)/2)+1]

                # Reshaping the 2D array of the sliced neighbourhood to make the median finding process easier
                slicedNeighbourhood = np.reshape(slicedNeighbourhood, kernelSize**2)
                # Looping on the neighbourhood with half of its size - 1 number of iterations,
                # In each iteration, the minimum of the array is found and is deleted from it (if there is more than one minimum, only one is taken which is the first)
                # So that the next taken minimum from the left values in the array will be its median value
                for x in range(int(kernelSize**2/2)):
                    indexOfMinimumValue = np.where(slicedNeighbourhood == np.min(slicedNeighbourhood))[0]
                    if len(indexOfMinimumValue) == 1: slicedNeighbourhood = np.delete(slicedNeighbourhood, indexOfMinimumValue)
                    elif len(indexOfMinimumValue) > 1:slicedNeighbourhood = np.delete(slicedNeighbourhood, indexOfMinimumValue[0])
                neighbourhoodMedian = np.min(slicedNeighbourhood)

                # Placing median in the location of the targetted pixel at hand in the resulted denoised image array (which is not padded)
                denoisedImage[i-int((kernelSize-1)/2), j-int((kernelSize-1)/2)] = neighbourhoodMedian

        # Clearing Old Image and Displaying New One on Figure
        self.denoisedImageFigure.figimage(denoisedImage, resize=False, cmap='gray', vmin=0, vmax=2**(self.imageBitDepth)-1)
        denoisedImageCanvas = FigureCanvas(self.denoisedImageFigure)
        self.ui.denoisedImageGridLayout.addWidget(denoisedImageCanvas, 0, 0, 1, 1)
        

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