
                                                                    # # # # # # # # # # Imports # # # # # # # # # #

import warnings
warnings.filterwarnings('ignore')
import sys
import math
import numpy as np
from GUI import Ui_MainWindow
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


                                                                # # # # # # # # # # Window Declaration # # # # # # # # # #


class MainWindow(QMainWindow):

    # Window Constructor
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)


                                                        # # # # # # # # # # Linking GUI Elements to Methods # # # # # # # # # #


        self.ui.noiseTypeComboBox.currentTextChanged.connect(self.AddNoiseToImage)


                                                        # # # # # # # # # # Class Variables Initialization # # # # # # # # # #

        # GUI figures initialization
        self.originalImageFigure = plt.figure(); self.noisyImageFigure = plt.figure(); self.selectedROIImageFigure = plt.figure(); self.ROIHistogramFigure = plt.figure()
        # Combining related GUI elements into lists
        self.ROIRelatedElements, self.ROIRelatedStatistics, self.ROIRelatedFigures = [self.ui.selectedROILabel, self.ui.ROIHistogramLabel, self.ui.ROIMeanLabel, self.ui.ROIStandardDeviationLabel], [self.ui.ROIMeanData, self.ui.ROIStandardDeviationData], [self.selectedROIImageFigure, self.ROIHistogramFigure]
        # Generating original image and initially hiding ROI-related GUI elements
        self.GenerateOriginalImage(); self.ui.noisyImageLabel.hide()
        for uiElement in self.ROIRelatedElements: uiElement.hide()


                                                            # # # # # # # # # # Class Methods Declaration # # # # # # # # # #
  

    # Display a Generated Image with Various Shapes and Intensities
    def GenerateOriginalImage(self):

        try:
            # Form an image with intensity values between 0-255, consisting of 50-intensity pixel border,
            # 120-intensity square and 200-intensity circle
            self.originalImage = np.zeros((256, 256))
            self.originalImage[:, :] = 50; self.originalImage[37:217, 36:218] = 120
            rowIndices, columnIndices = np.indices(self.originalImage.shape)
            circleLocations = (((rowIndices - 128)**2) + ((columnIndices - 127)**2)) <= (60**2)
            self.originalImage[circleLocations] = 200
            # Image display
            self.DisplayImage(self.originalImageFigure, self.originalImage, self.ui.originalImageGridLayout)
        except: self.ShowErrorMessage("Something Went Wrong in Original Image Generation!      ")


    # Display Noisy Image According To User Choice of Noise Type
    def AddNoiseToImage(self):

        try:
            # Construct a noise image with same size as original image to for their addition operation
            # and assign noise type according to user choice
            self.noisyImage = np.zeros((256, 256))
            if self.ui.noiseTypeComboBox.currentText() == "Gaussian Noise": noise = np.random.normal(loc=0, scale=5, size=(256, 256))
            elif self.ui.noiseTypeComboBox.currentText() == "Uniform Noise": noise = np.random.uniform(low=-10, high=10, size=(256, 256))
            else: return
            # Clear ROI related figures from previous data
            for figure in self.ROIRelatedFigures: figure.clear(); figure.canvas.draw()
            for statistic in self.ROIRelatedStatistics: statistic.setText('')
            # Add noise to image and display result
            self.noisyImage = self.originalImage + noise
            self.ui.noisyImageLabel.show(); self.DisplayImage(self.noisyImageFigure, self.noisyImage, self.ui.noisyImageGridLayout, True)
        except: self.ShowErrorMessage("Something Went Wrong in Adding Noise To Image!      ")


    # Allow User to Select ROI on Noisy Image and Form Required Processing
    def SelectROI(self, eclick, erelease):

        try:
            # If user did not choose noise type, no operation will be done on selected ROI
            if self.ui.noiseTypeComboBox.currentText() == "Choose Noise Type": return
            # Fetch extents of selected ROI in x and y dimensions, and slice the ROI accordingly from the original image
            ROIExtents = self.selectedROI.extents
            yMin, yMax, xMin, xMax = round(ROIExtents[0]), round(ROIExtents[1]), round(ROIExtents[2]), round(ROIExtents[3])
            self.slicedROI = self.noisyImage[xMin:xMax+1, yMin:yMax+1]
            # Show ROI-related GUI elements, form its histogram and calculate its statistics
            for uiElement in self.ROIRelatedElements: uiElement.show(); self.DisplayImage(self.selectedROIImageFigure, self.slicedROI, self.ui.selectedROIImageGridLayout)
            self.ConstructROIHistogram(); self.CalculateHistogramStatistics()
        except: self.ShowErrorMessage("Something Went Wrong in ROI Processing!      ")


    # Display and Calculate Histogram Selected ROI
    def ConstructROIHistogram(self):

        # Construct an array of all graylevel intensities that can be available in ROI, an another for their frequencies in ROI
        self.ROIGrayLevelIntensities, self.ROIGrayLevelFrequencies = np.arange(0, 256, 1), np.zeros((256))

        # Looping on each pixel intensity in ROI and incrementing corresponding intensity in array of intensity frequencies
        for i in range(self.slicedROI.shape[0]):
            for j in range(self.slicedROI.shape[1]):
                self.ROIGrayLevelFrequencies[round(self.slicedROI[i, j])] += 1
        # Normalise frequencies using ROI size
        self.ROINormalisedGrayLevelFrequencies = self.ROIGrayLevelFrequencies / int(self.slicedROI.shape[0] * self.slicedROI.shape[1])

        # Clearing old histogram and displaying new one on figure
        self.ROIHistogramFigure.clear(); self.ROIHistogramFigure.canvas.draw(); axes = self.ROIHistogramFigure.add_subplot()
        axes.bar(self.ROIGrayLevelIntensities, self.ROINormalisedGrayLevelFrequencies); axes.set_xlim(0, 255)
        histogramCanvas = FigureCanvas(self.ROIHistogramFigure); self.ui.ROIHistogramGridLayout.addWidget(histogramCanvas, 0, 0, 1, 1)
        

    # Display and Calculate ROI Statistics from its Histogram
    def CalculateHistogramStatistics(self):

        # Initialising statistics to be calculated
        ROIMean, ROIStandardDeviation = 0, 0
        # Calculating mean by multiplying intensity value with its normalised frequency, and obtaining sum for all frequencies
        for intensity in self.ROIGrayLevelIntensities: ROIMean += (intensity * self.ROINormalisedGrayLevelFrequencies[intensity])
        # Calculating standard deviation by multiplying difference between intensity and ROI mean squared with its normalised frequency and obtaining sum
        # Then, taking square root of this varinace
        for intensity in self.ROIGrayLevelIntensities: ROIStandardDeviation += (((intensity - ROIMean)**2) * self.ROINormalisedGrayLevelFrequencies[intensity])
        ROIStandardDeviation = math.sqrt(ROIStandardDeviation)
        # Display statistics
        self.ui.ROIMeanData.setText(str(round(ROIMean, 1))); self.ui.ROIStandardDeviationData.setText(str(round(ROIStandardDeviation, 1)))


                                                                # # # # # # # # # # Helper Functions # # # # # # # # # #


    # Display Passed Image on Matplotlib Canvas and Determine If It Should be Interactive
    def DisplayImage(self, imageFigure, imageToDisplay, gridLayout, interactive=False):

        # Clearing canvas, and drawing a new subplot
        imageFigure.clear(); imageFigure.canvas.draw()
        axes = imageFigure.add_subplot(); axes.xaxis.set_ticks_position('top')
        imageCanvas = FigureCanvas(imageFigure); gridLayout.addWidget(imageCanvas, 0, 0, 1, 1)
        # Providing that an image is interactive, allow user to select an ROI through left-mouse dragging,
        # and perform required processing on it through assigning the resulted ROI with 'self.SelectROI' function
        if interactive: self.selectedROI = RectangleSelector(axes, self.SelectROI, drawtype='box', button=[1])
        axes.imshow(imageToDisplay, cmap="gray", origin='upper', vmin=0, vmax=255)


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