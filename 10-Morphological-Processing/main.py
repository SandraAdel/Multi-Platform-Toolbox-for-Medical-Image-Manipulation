
                                                                    # # # # # # # # # # Imports # # # # # # # # # #


import warnings
warnings.filterwarnings('ignore')
import sys
import cv2
import numpy as np
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


                                                        # # # # # # # # # # Linking GUI Elements to Methods # # # # # # # # # #


        self.ui.morphologicalProcessComboBox.currentTextChanged.connect(self.ApplyMorphologicalOperation)


                                                        # # # # # # # # # # Class Variables Initialization # # # # # # # # # #


        # GUI figures initialization
        self.originalImageFigure = plt.figure()
        self.morphologicalProcessImageFigure = plt.figure()
        self.bestNoiseRemovalImageFigure = plt.figure()

        # Generating original image to apply morphological processes on and its verion of best noise removal
        self.DisplayOriginalImage()
        self.DisplayBestNoiseRemovalImage()


                                                            # # # # # # # # # # Class Methods Declaration # # # # # # # # # #
  

    # Read Image To Perform Morphological Processes On
    def DisplayOriginalImage(self):
        # Read binary image to apply morphological processes on, and normalise its values to 0 and 1, instead of 0 and 255
        self.originalImage = cv2.imread('binary_image.png', cv2.IMREAD_GRAYSCALE) // 255
        self.DrawNewFigure(self.originalImageFigure, self.originalImage, self.ui.originalImageGridLayout)


    # Apply Erosion Or Dilation On Passed Image Using Passed Structuring Element
    def ErodeOrDilate(self, operationName, imageToPerformProcessOn, structuringElement):

        # Initialise an empty array with same shape of original image to store output of morphological process in
        morphologicalProcessImage = np.zeros((imageToPerformProcessOn.shape[0], imageToPerformProcessOn.shape[1]))
        # Counting number of foreground pixels in structuring element to compare against while traversing on image with it in morphological operation
        structuringElementForegroundPixelsCount = 0
        for element in np.nditer(structuringElement): structuringElementForegroundPixelsCount += element

        # Image Padding:
        # Create an empty array of size equals that of the original image in addition to the padding, which is equal to structuring element size - 1 for both the rows and columns
        # (row shape of structuring element-1)/2 extra row at top and bottom of image, and (column shape of structuring element-1)/2 extra column at beginning and end of image
        # and placing the image values in the middle of the padded image
        self.paddedImage = np.zeros((imageToPerformProcessOn.shape[0]+(structuringElement.shape[0]-1), imageToPerformProcessOn.shape[1]+(structuringElement.shape[1]-1)))
        self.paddedImage[int((structuringElement.shape[0]-1)/2):-int((structuringElement.shape[1]-1)/2), int((structuringElement.shape[0]-1)/2):-int((structuringElement.shape[1]-1)/2)] = imageToPerformProcessOn

        # Looping on original image values in padded image (structuring element center point at image values leaving aside padded values)
        for i in range(int((structuringElement.shape[0]-1)/2), self.paddedImage.shape[0] - int((structuringElement.shape[0]-1)/2)):
            for j in range(int((structuringElement.shape[1]-1)/2), self.paddedImage.shape[1] - int((structuringElement.shape[1]-1)/2)):

                # Slicing the neighbourhood of the targetted pixel at hand according to structuring element size
                slicedNeighbourhood = self.paddedImage[i-int((structuringElement.shape[0]-1)/2):i+int((structuringElement.shape[1]-1)/2)+1, j-int((structuringElement.shape[0]-1)/2):j+int((structuringElement.shape[1]-1)/2)+1]

                # Traversing on neighbourhood pixels underneath the structuring element, and counting the number of times a foreground pixel in the structuring element meets
                # a corresponding foreground pixel in the neighbourhood
                neighbourhoodForegroundPixelsCount = 0
                for a in range(structuringElement.shape[0]):
                    for b in range(structuringElement.shape[1]):
                        if structuringElement[a, b] == 1 and slicedNeighbourhood[a, b] == 1: neighbourhoodForegroundPixelsCount += 1

                # If the process is Erosion, and number of times of matching a foreground pixel in the structuring element with a corresponding one in image neighbourhood
                # is exactly equal to the number of foreground pixels in the structuring element itself, that means it fits inside the object
                # So, the corresponding pixel in resulted image is assigned with one, else zero
                if operationName == 'Erode':
                    if neighbourhoodForegroundPixelsCount == structuringElementForegroundPixelsCount: elementToBePlaced = 1
                    else: elementToBePlaced = 0
                # If the process is Dilation, and number of times of matching a foreground pixel in the structuring element with a corresponding one in image neighbourhood
                # is less than or equal to the number of foreground pixels in the structuring element itself but greater than zero, that means it hits the object at least one of its foreground elements
                # So, the corresponding pixel in resulted image is assigned with one, else zero
                elif operationName == 'Dilate':
                    if neighbourhoodForegroundPixelsCount <= structuringElementForegroundPixelsCount and neighbourhoodForegroundPixelsCount > 0: elementToBePlaced = 1
                    else: elementToBePlaced = 0
                
                morphologicalProcessImage[i-int((structuringElement.shape[0]-1)/2), j-int((structuringElement.shape[1]-1)/2)] = elementToBePlaced
        # Returning resulted image for further processing or display
        return morphologicalProcessImage


    # Applying User Selection of Morphological Operation on Image Basically Built on Erosion and Dilation
    def ApplyMorphologicalOperation(self):

        # Try block of applying morphological process, if something went wrong, an error message is displayed to the user
        try:
            # Define structuring element to be used (exactly as in task statement)
            structuringElement = np.array([[0, 1, 1, 1, 0],
                                           [1, 1, 1, 1, 1],
                                           [1, 1, 1, 1, 1],
                                           [1, 1, 1, 1, 1],
                                           [0, 1, 1, 1, 0]])

            # Apply morphological process according to user selection
            # Erosion and Dilation are applied directly using 'ErodeOrDilate' function
            # Opening is achieved by applying Erosion followed by Dilation
            # Closing is achieved by applying Dilation followed by Erosion
            if self.ui.morphologicalProcessComboBox.currentText() == 'Erosion': morphologicalProcessImage = self.ErodeOrDilate('Erode', self.originalImage, structuringElement)
            elif self.ui.morphologicalProcessComboBox.currentText() == 'Dilation': morphologicalProcessImage = self.ErodeOrDilate('Dilate', self.originalImage, structuringElement)
            elif self.ui.morphologicalProcessComboBox.currentText() == 'Opening':
                morphologicalProcessImage = self.ErodeOrDilate('Erode', self.originalImage, structuringElement)
                morphologicalProcessImage = self.ErodeOrDilate('Dilate', morphologicalProcessImage, structuringElement)
            elif self.ui.morphologicalProcessComboBox.currentText() == 'Closing':
                morphologicalProcessImage = self.ErodeOrDilate('Dilate', self.originalImage, structuringElement)
                morphologicalProcessImage = self.ErodeOrDilate('Erode', morphologicalProcessImage, structuringElement)
            else: return

            # Displaying image after applying morphological process on GUI
            self.ui.morphologicalProcessImageLabel.setText(self.ui.morphologicalProcessComboBox.currentText())
            self.DrawNewFigure(self.morphologicalProcessImageFigure, morphologicalProcessImage, self.ui.morphologicalProcessImageGridLayout)

        except: self.ShowErrorMessage("Something Went Wrong in Applying Morphological Operation!      ")


    # Apply Algorithm That Best Removes Noise From Image and Display It
    def DisplayBestNoiseRemovalImage(self):

        try:
            # Defining structuring element to be used that best removes noise from image (BY TRIAL)
            structuringElement = np.array([[0, 1, 0],
                                           [1, 1, 1],
                                           [0, 1, 0]])

            # Applying Opening followed by Closing on noisy image using structuring element defined above
            # Opening reduces most noise components in both background and fingerprint itself
            # but creates new gaps between fingerprint ridges which are by Closing
            morphologicalProcessImage = self.ErodeOrDilate('Erode', self.originalImage, structuringElement)
            morphologicalProcessImage = self.ErodeOrDilate('Dilate', morphologicalProcessImage, structuringElement)
            morphologicalProcessImage = self.ErodeOrDilate('Dilate', morphologicalProcessImage, structuringElement)
            bestNoiseRemovalImage = self.ErodeOrDilate('Erode', morphologicalProcessImage, structuringElement)

            # Displaying best noise removal image on GUI
            self.DrawNewFigure(self.bestNoiseRemovalImageFigure, bestNoiseRemovalImage, self.ui.bestNoiseRemovalImageGridLayout)

        except: self.ShowErrorMessage("Something Went Wrong in Displaying Best Noise Removal Image!      ")


                                                                # # # # # # # # # # Helper Functions # # # # # # # # # #


    # Clear Figure of Old Image and Display New One
    def DrawNewFigure(self, figureToBeDrawOn, imageToDraw, figureGridLayout):
        # Clearing old figure
        figureToBeDrawOn.clear(); figureToBeDrawOn.canvas.draw()
        # Displaying new image
        figureToBeDrawOn.figimage(imageToDraw, resize=False, cmap='gray')
        figureCanvas = FigureCanvas(figureToBeDrawOn)
        figureGridLayout.addWidget(figureCanvas, 0, 0, 1, 1)


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