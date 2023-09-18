
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
        # Initially disable use of filtering button unless a user opens an image
        self.ui.lowpassFilterationPushButton.setEnabled(False)

        # Initialising Image Figure on Gridlayout Once at First for Image to be Displayed on (Tab 1)
        self.imageFigure = plt.figure()
        # Initialising Image Figures on Gridlayout Once at First for Image to be Displayed on (Tab 2)
        self.originalImageFigure = plt.figure()
        self.imageFourierSpectrumFigure = plt.figure()
        self.spatialKernelFigure = plt.figure()
        self.fourierKernelFigure = plt.figure()
        self.spatialFilterationFigure = plt.figure()
        self.fourierFilterationFigure = plt.figure()
        self.filteredSpectrumFigure = plt.figure()
        self.filterationDifferenceFigure = plt.figure()
        # Combining figures to be cleared in tab 2 each time a user opens a new image
        self.tab2FilterationFigures = [self.spatialKernelFigure, self.fourierKernelFigure, self.spatialFilterationFigure, self.fourierFilterationFigure, self.filteredSpectrumFigure, self.filterationDifferenceFigure]
        # Initialising Image Figures on Gridlayout Once at First for Image to be Displayed on (Tab 3)
        self.noisyImageFigure = plt.figure()
        self.noisyFourierSpectrumFigure = plt.figure()
        self.fourierFilterFigure = plt.figure()
        self.filteredImageFigure = plt.figure()


                                                        # # # # # # # # # # Linking GUI Elements to Methods # # # # # # # # # #


        self.ui.reisizeImageRadiobutton.toggled.connect(self.ResizeImage)
        self.ui.actionOpen_Image.triggered.connect(lambda: self.OpenImage())
        self.ui.lowpassFilterationPushButton.clicked.connect(self.FilterInSpatialAndFrequencyDomains)


                                                        # # # # # # # # # # Initial Show & Hide of UI Elements # # # # # # # # # #


        self.ui.reisizeImageRadiobutton.hide()
        self.ShowAndHideGUISettings("hide", self.generalImageInfoLabels)
        self.ShowAndHideGUISettings("hide", self.dicomSpecificImageInfoLabels)


                                                            # # # # # # # # # # Class Methods Declaration # # # # # # # # # #


                                                          # # # # # # # Using Tab 1, Tab 2, Tab 3Functionalities # # # # # # # #
                                                                    

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

            # Spatial and Fourier Filtering Try Block, If Carried Out Incorrectly, Error Message Pops Up
            try:
                # TAB 2
                # Enable filtering push button as user has opened an image to work on
                self.ui.lowpassFilterationPushButton.setEnabled(True)
                # Clear old figures related to previous opened image
                self.ClearFiguresList(self.tab2FilterationFigures)
                # Display grayscale version of opened image along with its spectrum
                self.DisplayGrayScaleVersionAndSpectrum()
            except: self.ShowErrorMessage("Something Wrong in Spatial or Fourier Filtering!      ")

            # Removing Periodic Noise Try Block, If Carried Out Incorrectly, Error Message Pops Up 
            # TAB 3
            try: self.RemovePeriodicNoise()
            except: self.ShowErrorMessage("Something Wrong in Removing Periodic Noise!      ")

        except: self.ShowErrorMessage("Something Wrong in Opening or Reading Image!      ")



                                                            # # # # # # # # # # Tab 2 Functionalities # # # # # # # # # # #

    def FilterInSpatialAndFrequencyDomains(self):
        
        # If user input of kernel size is invalid, output an error message and do not perform filtering
        self.kernelSize = int(self.ui.lowpassFilterationKernelSizeSpinbox.text())
        if (int(self.ui.lowpassFilterationKernelSizeSpinbox.text()) <= 0) or (int(self.ui.lowpassFilterationKernelSizeSpinbox.text()) == 1) or (int(self.ui.lowpassFilterationKernelSizeSpinbox.text()) % 2 == 0):
            self.ShowErrorMessage("Invalid Kernel Size!      "); return

        # Clear figures between iterations of filtering process
        self.ClearFiguresList(self.tab2FilterationFigures)
        # Blur image in spatial domain
        self.ApplySpatialFilteration()
        # Prepare low pass kernel to be used, and blur image in fourier domain
        self.PadAndDisplayLowpassKernel()
        self.ApplyFourierFilteration()
        # Show difference between both filtered images (None --> It is the same operation whether performed in spatial or frequency domains)
        self.DisplayFilterationDifference()


    # Filter Image in Spatial Domain Using Lowpass Kernel
    def ApplySpatialFilteration(self):

        # Initialise an empty array with same shape of original image to store output of low pass filter in, resulting in a blurred image
        self.spatialFilteredImage = np.zeros((self.grayScaleVersion.shape[0], self.grayScaleVersion.shape[1]))

        # Image Padding:
        # Create an empty array of size equals that of the original image in addition to the padding, which is equal to kernel size - 1 for both the rows and columns
        # (m-1)/2 extra row at top and bottom of image, and (n-1)/2 extra column at beginning and end of image
        # and placing the image values in the middle of the padded image
        self.paddedImage = np.zeros((self.grayScaleVersion.shape[0]+(self.kernelSize-1), self.grayScaleVersion.shape[1]+(self.kernelSize-1)))
        self.paddedImage[int((self.kernelSize-1)/2):-int((self.kernelSize-1)/2), int((self.kernelSize-1)/2):-int((self.kernelSize-1)/2)] = self.grayScaleVersion

        # Looping on original image values in padded image (kernel center point at image values leaving aside padded values)
        for i in range(int((self.kernelSize-1)/2), self.paddedImage.shape[0] - int((self.kernelSize-1)/2)):
            for j in range(int((self.kernelSize-1)/2), self.paddedImage.shape[1] - int((self.kernelSize-1)/2)):

                # Slicing the neighbourhood of the targetted pixel at hand according to kernel size
                slicedNeighbourhood = self.paddedImage[i-int((self.kernelSize-1)/2):i+int((self.kernelSize-1)/2)+1, j-int((self.kernelSize-1)/2):j+int((self.kernelSize-1)/2)+1]

                # Summing all values of neighbourhood, and placing result divided by number of pixels in the box kernel
                # in the location of the targetted pixel at hand in the resulted blurred image array (which is not padded)
                neighbourhoodSum = 0
                for element in np.nditer(slicedNeighbourhood): neighbourhoodSum += element
                self.spatialFilteredImage[i-int((self.kernelSize-1)/2), j-int((self.kernelSize-1)/2)] = neighbourhoodSum/(self.kernelSize**2)

        # Displaying spatially filtered image
        self.DrawNewFigure(self.spatialFilterationFigure, self.spatialFilteredImage, 'Spacial Unscaled', self.ui.spatialFilterationGridLayout)


    # Calculate and Show Grayscale Version of Image Along with Its Spectrum in Tab 2 of GUI
    def DisplayGrayScaleVersionAndSpectrum(self):

        # Constructing Grayscale Version of Image with Same Size as Original Image
        self.grayScaleVersion = np.zeros((self.imageData.shape[0], self.imageData.shape[1]))
        # If Image is RGB, Transform it into Grayscale
        if len(self.imageData.shape) == 3: self.grayScaleVersion = np.round((0.2989 * self.imageData[:, :, 0]) + (0.5870 * self.imageData[:, :, 1]) + (0.1140 * self.imageData[:, :, 2])).astype('int')
        # If Image is Already Grayscale, Assign it as It is
        elif len(self.imageData.shape) == 2: self.grayScaleVersion = self.imageData

        # Transform image into frequency domain and apply fftshift for centerlisation (for view to be -pi to pi instead of 0 to 2pi)
        self.imageFourierTransform = np.fft.fft2(self.grayScaleVersion); self.imageFourierTransform = np.fft.fftshift(self.imageFourierTransform)

        # Drawing image figure and its fourier spectrum
        self.DrawNewFigure(self.originalImageFigure, self.grayScaleVersion, 'Spacial Scaled', self.ui.originalImageGridLayout)
        self.DrawNewFigure(self.imageFourierSpectrumFigure, np.abs(self.imageFourierTransform), 'Fourier', self.ui.imageFourierSpectrumGridLayout)


    # Contsruct Padded Lowpass Kernel for Fourier Filteration and Display it
    def PadAndDisplayLowpassKernel(self):

        # Construct 2D array of the box kernel to be applied
        boxKernel = np.ones((self.kernelSize, self.kernelSize))
        # Calculate number of rows and columns to be added on each side of the box kernel to make it equal in size to the image
        numberOfRowsToBePaddedOnEachSide, numberOfColumnsToBePaddedOnEachSide = math.floor((self.paddedImage.shape[0] - self.kernelSize)/2), math.floor((self.paddedImage.shape[1] - self.kernelSize)/2)
        # Pad box kernel so as to be equal to image to be filtered
        prefinalPaddedKernel = np.zeros((numberOfRowsToBePaddedOnEachSide*2 + self.kernelSize, numberOfColumnsToBePaddedOnEachSide*2 + self.kernelSize))
        prefinalPaddedKernel[numberOfRowsToBePaddedOnEachSide:-numberOfRowsToBePaddedOnEachSide, numberOfColumnsToBePaddedOnEachSide:-numberOfColumnsToBePaddedOnEachSide] = boxKernel

        # The number of rows or columns to be added might be odd, which results in kernel being not equal to image size (If so, then less here because floor was used in the calculation)
        # If the kernel is less with an extra row and/or column than the image, the final version of the kernel is dealt with accordingly to as to match sizes of both kernel and image
        # If both size are equal from the beginning, then the final version of the kernel holds no change
        greaterRowsNumber, greaterColumnsNumber = max(prefinalPaddedKernel.shape[0], self.paddedImage.shape[0]), max(prefinalPaddedKernel.shape[1], self.paddedImage.shape[1])
        paddedKernel = np.zeros((greaterRowsNumber, greaterColumnsNumber))
        paddedKernel[np.absolute(prefinalPaddedKernel.shape[0] - self.paddedImage.shape[0]):, np.absolute(prefinalPaddedKernel.shape[1] - self.paddedImage.shape[1]):] = prefinalPaddedKernel

        # Transform kernel into frequency domain and apply fftshift for centerlisation (for view to be -pi to pi instead of 0 to 2pi)
        self.kernelFourierTransform = np.fft.fft2(paddedKernel); self.kernelFourierTransform = np.fft.fftshift(self.kernelFourierTransform)

        # Drawing kernel figure and its fourier spectrum
        self.DrawNewFigure(self.spatialKernelFigure, paddedKernel, 'Spacial Unscaled', self.ui.lowpassSpatialKernelGridLayout)
        self.DrawNewFigure(self.fourierKernelFigure, np.abs(self.kernelFourierTransform), 'Fourier', self.ui.lowpassFourierKernelGridLayout)


    # Filter Image in Fourier Domain Using Lowpass Kernel
    def ApplyFourierFilteration(self):

        # Transform padded image used in spatial filteration into frequency domain and apply fftshift for centerlisation (for view to be -pi to pi instead of 0 to 2pi)
        imageFourierTransform = np.fft.fft2(self.paddedImage); imageFourierTransform = np.fft.fftshift(imageFourierTransform)

        # Apply elementwise multiplication between fourier transform of image and padded kernel, and display result
        self.fourierFilteredImage = np.multiply(imageFourierTransform, self.kernelFourierTransform)
        self.DrawNewFigure(self.filteredSpectrumFigure, np.abs(self.fourierFilteredImage), 'Fourier', self.ui.filteredSpectrumGridLayout)
        
        # Transform filtered image into spatial domain, and remove the padding previously applied
        self.fourierFilteredImage = np.fft.ifftshift(self.fourierFilteredImage); self.fourierFilteredImage = np.fft.ifft2(self.fourierFilteredImage).real; self.fourierFilteredImage = np.fft.fftshift(self.fourierFilteredImage)
        self.fourierFilteredImage = self.fourierFilteredImage[int((self.kernelSize-1)/2):-int((self.kernelSize-1)/2), int((self.kernelSize-1)/2):-int((self.kernelSize-1)/2)]

        # Display fourier filtered image
        self.DrawNewFigure(self.fourierFilterationFigure, self.fourierFilteredImage, 'Spacial Unscaled', self.ui.fourierFilterationGridLayout)


    # Display Difference Between Filteration Operation in Both Spatial and Frequency Domains
    def DisplayFilterationDifference(self):

        # Recale image versions filtered both in frequency and spatial domains
        self.fourierFilteredImage = np.round( ((self.fourierFilteredImage - np.min(self.fourierFilteredImage)) / (np.max(self.fourierFilteredImage) - np.min(self.fourierFilteredImage))) * (2**(self.imageBitDepth)-1) )
        self.spatialFilteredImage = np.round( ((self.spatialFilteredImage - np.min(self.spatialFilteredImage)) / (np.max(self.spatialFilteredImage) - np.min(self.spatialFilteredImage))) * (2**(self.imageBitDepth)-1) )
        # Calculate and display differnce between the output of both operations
        filterationDifference = np.subtract(self.fourierFilteredImage, self.spatialFilteredImage)
        print(filterationDifference)
        self.DrawNewFigure(self.filterationDifferenceFigure, filterationDifference, 'Spacial Scaled', self.ui.filterationDifferenceGridLayout)


                                                            # # # # # # # # # # Tab 3 Functionalities # # # # # # # # # # #


    # Apply Notch Filter in Image with Periodic Noise to Remove Moiree Patterns
    def RemovePeriodicNoise(self):

        # Read image with periodic noise and transform it into grayscale
        periodicNoiseData = cv2.imread('Periodic_Noise.jpg', -1)
        periodicNoiseData = np.round((0.2989 * periodicNoiseData[:, :, 0]) + (0.5870 * periodicNoiseData[:, :, 1]) + (0.1140 * periodicNoiseData[:, :, 2])).astype('int')
        # Transform noisy image into fourier domain, and apply fftshift for centerlisation (for view to be -pi to pi instead of 0 to 2pi)
        noisyImageFourierTransform = np.fft.fft2(periodicNoiseData); noisyImageFourierTransform = np.fft.fftshift(noisyImageFourierTransform)

        # Construct notch filter to remove the moiree patterns from the image in spatial domain which appear as burst-like impulses in frequency domain
        # that are symetric due to near periodicity of the moiree pattern
        # These bursts are removed by multiplying image spectrum with a mask of ones containing zeros at the positions of the impulse bursts
        notchFilter = np.ones((periodicNoiseData.shape[0], periodicNoiseData.shape[1]))
        notchFilter[153:173, 142:152] = 0; notchFilter[153:173, 200:210] = 0; notchFilter[230:250, 142:152] = 0; notchFilter[230:250, 200:210] = 0
        notchFilter[280:290, 143:153] = 0; notchFilter[275:285, 200:210] = 0; notchFilter[120:130, 141:151] = 0; notchFilter[113:123, 197:207] = 0
        notchFilter[77:83, 144:149] = 0; notchFilter[73:79, 202:207] = 0; notchFilter[321:327, 144:149] = 0; notchFilter[318:324, 202:207] = 0
        notchFilter[34:38, 202:208] = 0; notchFilter[35:40, 144:149] = 0; notchFilter[360:366, 202:207] = 0; notchFilter[362:368, 145:150] = 0
        
        # Filter Image by multiplying image spectrum with mask, and display result
        filteredImage = np.multiply(noisyImageFourierTransform, notchFilter)
        self.DrawNewFigure(self.fourierFilterFigure, np.abs(filteredImage), 'Fourier', self.ui.fourierFilterGridLayout)
        
        # Transform image into spatial domain and display it
        filteredImage = np.fft.ifftshift(filteredImage); filteredImage = np.fft.ifft2(filteredImage).real
        self.DrawNewFigure(self.noisyImageFigure, periodicNoiseData, 'Spacial Unscaled', self.ui.noisyImageGridLayout)
        self.DrawNewFigure(self.noisyFourierSpectrumFigure, np.abs(noisyImageFourierTransform), 'Fourier', self.ui.noisyFourierSpectrumGridLayout)
        self.DrawNewFigure(self.filteredImageFigure, filteredImage, 'Spacial Unscaled', self.ui.filteredImageGridLayout)


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

    # Clear Figure of Old Image and Display New One
    def DrawNewFigure(self, figureToBeDrawOn, imageToDraw, imageDomain, figureGridLayout):
        # If image was in fourier domain, apply log compression and rescale image. If it was in spatial domain and needs to be rescaled, perform so.
        if imageDomain == 'Fourier':
            imageToDraw = np.log(imageToDraw + 1); imageToDraw = np.round( ((imageToDraw - np.min(imageToDraw)) / (np.max(imageToDraw) - np.min(imageToDraw))) * (2**(self.imageBitDepth)-1) )
        elif imageDomain == 'Spacial Unscaled': imageToDraw = np.round( ((imageToDraw - np.min(imageToDraw)) / (np.max(imageToDraw) - np.min(imageToDraw))) * (2**(self.imageBitDepth)-1) )
        # Clearing old figure
        figureToBeDrawOn.clear(); figureToBeDrawOn.canvas.draw()
        # Displaying new image
        figureToBeDrawOn.figimage(imageToDraw, resize=False, cmap='gray', vmin=0, vmax=2**(self.imageBitDepth)-1)
        figureCanvas = FigureCanvas(figureToBeDrawOn)
        figureGridLayout.addWidget(figureCanvas, 0, 0, 1, 1)

    # Clear List of Figures All at Once
    def ClearFiguresList(self, figuresList):
        for figure in figuresList:
            figure.clear(); figure.canvas.draw()

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