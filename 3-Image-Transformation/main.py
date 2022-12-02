
                                                                    # # # # # # # # # # Imports # # # # # # # # # #


import sys
import math
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


        self.ui.applyTransformationPushButton.clicked.connect(self.ApplyTransformation)
        self.ui.transformationTypeComboBox.currentTextChanged.connect(self.AdjustUIElementsOnUserInput)
        self.ui.interpolationMethodComboBox.currentTextChanged.connect(self.AdjustUIElementsOnUserInput)


                                                        # # # # # # # # # # Class Variables Initialization # # # # # # # # # #


        self.originalImageFigure = plt.figure()
        self.transformedImageFigure = plt.figure()
        self.GenerateOriginalImage()


                                                            # # # # # # # # # # Class Methods Declaration # # # # # # # # # #
  

    # Construct Original 'T' Shaped Original Image To Perform Transformation On
    def GenerateOriginalImage(self):

        try:
            # Construct black image of size 128 x 128 pixels, and assign white pixels
            # in image center so that they form a 'T' shape
            self.originalImage = np.zeros((128, 128))
            self.originalImage[29:49, 29:99] = 1
            self.originalImage[49:99, 54:74] = 1
            self.DisplayImage(self.originalImageFigure)
        except: self.ShowErrorMessage("Something Went Wrong in Original Image Generation!      ")


    # Change UI Element's Enability According To User's Input To Handle Exceptions
    def AdjustUIElementsOnUserInput(self):

        # Enable spinbox for user to input rotation angle if he/she choose to perform rotation, but disable it in case of sheering
        if self.ui.transformationTypeComboBox.currentText() == "Rotation":
            self.ui.rotationAngleLabel.setEnabled(True)
            self.ui.rotationAngleSpinBox.setEnabled(True)
        elif self.ui.transformationTypeComboBox.currentText() == "Horizontal Sheering":
            self.ui.rotationAngleLabel.setEnabled(False)
            self.ui.rotationAngleSpinBox.setEnabled(False)

        # Onlu enable the 'Apply Transformation' button if the user's choices of transformation operation and interpolation method are valid
        if self.ui.transformationTypeComboBox.currentText() != "Choose Transformation Type" and self.ui.interpolationMethodComboBox.currentText() != "Choose Interpolation Method": self.ui.applyTransformationPushButton.setEnabled(True)
        else: self.ui.applyTransformationPushButton.setEnabled(False)


    # Construct Transformation Matrix to be Applied on Pixel Indices According to User's Choice of Transformation Operation
    def FormTransformationMatrix(self):

        # Since we map the transformed image to the original image, we perform the inverse of the transformation on the transformed image 
        # ad this is done to assign each pixel value independently without confusing pixel values together when re-distrubting them from original image to transformed image
        # (Ex: two pixels in original image assigned to same pixel in transformed image)

        if self.ui.transformationTypeComboBox.currentText() == "Rotation":

            # Negative of the rotation angle is taken to perform inverse rotation matrix
            rotationAngle = -(float(self.ui.rotationAngleSpinBox.text())*np.pi)/180
            transformationMatrix = np.array([[math.cos(rotationAngle), -math.sin(rotationAngle), 0],
                                             [math.sin(rotationAngle), math.cos(rotationAngle), 0],
                                             [0, 0, 1]])

            # Forming rotation illustration text label, indicating rotation angle and direction
            transformationIllustrationText = 'Rotating By '+str(abs(float(self.ui.rotationAngleSpinBox.text())))+' Degrees'
            if float(self.ui.rotationAngleSpinBox.text()) not in [0, 360, -360]: 
                if float(self.ui.rotationAngleSpinBox.text()) > 0: transformationIllustrationText = transformationIllustrationText + ' To The Left'
                elif float(self.ui.rotationAngleSpinBox.text()) < 0: transformationIllustrationText = transformationIllustrationText + ' To The Right'

        if self.ui.transformationTypeComboBox.currentText() == "Horizontal Sheering":

            # Since only horizontal sheering is required so that the vertical makes 45 degrees with positive direction of x-axis and 135 degrees with the negative direction,
            # sheering matrix is constructed with only the value of 0.5, put in negative since we want the inverse of the operation
            transformationMatrix = np.array([[1, 0, 0],
                                             [-0.5, 1, 0],
                                             [0, 0, 1]])

            # Forming sheering illustration text label, indicating sheering value and direction
            transformationIllustrationText = 'Sheering Horizontally with 45 Degrees'

        self.ui.transformationIllustrationLabel.setText(transformationIllustrationText)
        return transformationMatrix


    # Interpolate Pixel Intensity Value According To Its Location and User's Choice of Interpolation Method
    def ApplyInterpolation(self, i, j, mappedRowIndex, mappedColumnIndex):

        # If location of mapped pixel was entirely out of the grid of the original image, the pixel intensity will be left as zero (since transformed image is cropped)
        if (mappedRowIndex < 0 or mappedRowIndex > self.originalImage.shape[0]-1) or (mappedColumnIndex < 0 or mappedColumnIndex > self.originalImage.shape[1]-1): return
        
        if self.ui.interpolationMethodComboBox.currentText() == "Nearest Neighbour":
            
            # If the decimal part of the mapped index value was less than or equal to 0.5, mapped index is floored, otherwise ceiled
            # and the nearest pixel intensity is assigned to pixel in transformed image according to its mapped location in original image
            mappedRowIndex = math.floor(mappedRowIndex) if math.modf(mappedRowIndex)[0] <= 0.5 else math.ceil(mappedRowIndex)
            mappedColumnIndex = math.floor(mappedColumnIndex) if math.modf(mappedColumnIndex)[0] <= 0.5 else math.ceil(mappedColumnIndex)
            self.transformedImage[i, j] = self.originalImage[mappedRowIndex, mappedColumnIndex]

        if self.ui.interpolationMethodComboBox.currentText() == "Bilinear":

            # If Both Indices of Pixel Value in Scaled Image Mapped in Original Image are Integers, Pixel Value from Original Image is Directly Put in Scaled Image
            if (mappedRowIndex % 1 == 0) and (mappedColumnIndex % 1 == 0): self.transformedImage[i, j] = self.originalImage[int(mappedRowIndex), int(mappedColumnIndex)]
            # If Row Index of Pixel Value in Scaled Image Mapped in Original Image is Float But Column Index is Integer, Linear Interpolation is Performed Along Mapped Column in Original Image
            # In Calculated Column, Intensities of Both Row Index Floored and Ceiled are Fetched from Original Image, and Each is Multiplied by Its Opposite Distance from Float Row Index Value of Mapped Pixel Currently Calculated
            elif (mappedRowIndex % 1 != 0) and (mappedColumnIndex % 1 == 0): self.transformedImage[i, j] = (self.originalImage[math.floor(mappedRowIndex), int(mappedColumnIndex)] * (math.ceil(mappedRowIndex) - mappedRowIndex)) + (self.originalImage[math.ceil(mappedRowIndex), int(mappedColumnIndex)] * (mappedRowIndex - math.floor(mappedRowIndex)))
            # If Column Index of Pixel Value in Scaled Image Mapped in Original Image is Float But Row Index is Integer, Linear Interpolation is Performed Along Mapped Row in Original Image
            # In Calculated Row, Intensities of Both Column Index Floored and Ceiled are Fetched from Original Image, and Each is Multiplied by Its Opposite Distance from Float Row Index Value of Mapped Pixel Currently Calculated
            elif (mappedRowIndex % 1 == 0) and (mappedColumnIndex % 1 != 0): self.transformedImage[i, j] = (self.originalImage[int(mappedRowIndex), math.floor(mappedColumnIndex)] * (math.ceil(mappedColumnIndex) - mappedColumnIndex)) + (self.originalImage[int(mappedRowIndex), math.ceil(mappedColumnIndex)] * (mappedColumnIndex - math.floor(mappedColumnIndex)))
            # If Both Indices of Pixel Value in Scaled Image Mapped in Original Image are Floats, Bilinear Interpolation is Performed by Performing Three Operations of Linear Interpolation Using Its Four Nearest Neighbours in Original Image
            elif (mappedRowIndex % 1 != 0) and (mappedColumnIndex % 1 != 0):
            # Linear Interpolation is Performed Along First Row by Flooring Row Index, Fetching the First Two Neighbours of that Row by Flooring and Ceiling Column Value and Calculating Value of Pixel above Currently Handled Pixel in First Row
                firstRowIntermediateIntensity = ( self.originalImage[math.floor(mappedRowIndex), math.floor(mappedColumnIndex)] * (math.ceil(mappedColumnIndex) - mappedColumnIndex) ) + ( self.originalImage[math.floor(mappedRowIndex), math.ceil(mappedColumnIndex)] * (mappedColumnIndex - math.floor(mappedColumnIndex)) )
                # Linear Interpolation is Performed Along Second Row by Ceiling Row Index, Fetching the Second Two Neighbours of that Row by Flooring and Ceiling Column Value and Calculating Value of Pixel below Currently Handled Pixel in Second Row
                secondRowIntermediateIntensity = ( self.originalImage[math.ceil(mappedRowIndex), math.floor(mappedColumnIndex)] * (math.ceil(mappedColumnIndex) - mappedColumnIndex) ) + ( self.originalImage[math.ceil(mappedRowIndex), math.ceil(mappedColumnIndex)] * (mappedColumnIndex - math.floor(mappedColumnIndex)) )
                # Linear Interpolation is Performed Using Intermediate Intensity Values Previously Calculated Along Column Combining Locations of Both Pixel and that Currently Handled
                self.transformedImage[i, j] = (firstRowIntermediateIntensity * (math.ceil(mappedRowIndex) - mappedRowIndex)) + (secondRowIntermediateIntensity * (mappedRowIndex - math.floor(mappedRowIndex)))


    # Forming User's Choice of Transformed Image
    def ApplyTransformation(self):

        try:
            # Constructing transformed image of same dimensions as original image
            self.transformedImage = np.zeros((self.originalImage.shape[0], self.originalImage.shape[1]))

            # Both rotation and sheering operations require the image to be translated so that its center is at the origin, so as to perform the transformation
            # operation about the center of the image (in our case, the image is resembled to those used in medical field where image center is most important)
            # In this case, both translation and inverse translation  matrices are constructed to transform each pixel in the image before transforming its indices
            # so the the image center is at the origin
            translationMatrix = np.array([[1, 0, -(self.transformedImage.shape[0]-1)/2],
                                          [0, 1, -(self.transformedImage.shape[1]-1)/2],
                                          [0, 0, 1]])
            inverseTranslationMatrix = np.array([[1, 0, (self.transformedImage.shape[0]-1)/2],
                                                [0, 1, (self.transformedImage.shape[1]-1)/2],
                                                [0, 0, 1]])
            # A transformation matrix is obtained equivalent to the user's chosen transformation operation
            transformationMatrix = self.FormTransformationMatrix()

            # We loop on each pixel in the transformed image, map its location in the original image by applying the inverse of the transformation operation,
            # and interpolate its intensity value according to its mapped location in original image
            for i in range(self.transformedImage.shape[0]):
                for j in range(self.transformedImage.shape[1]):

                    # Constructing a matrix of the row and column indices of the pixel currently handled
                    pixelIndicesInTransformedImage = np.array([[i],
                                                               [j],
                                                               [1]])
                    # The following operation is performed to get the mapping of the pixel of transformed image in original image
                    # Mapped Indices (Original Image)= Inverse Translation Matrix x Transformation Matrix (Rotation or Sheering) x Translation Matrix x Pixel Indices (Transformed Image)
                    pixelIndicesMappedInOriginalImage = np.matmul(inverseTranslationMatrix, np.matmul(transformationMatrix, np.matmul(translationMatrix, pixelIndicesInTransformedImage)))
                    mappedRowIndex, mappedColumnIndex = pixelIndicesMappedInOriginalImage[0, 0], pixelIndicesMappedInOriginalImage[1, 0]
                    # Assigning pixel intensity value according to mapped pixel location and user's choice of interpolation method
                    self.ApplyInterpolation(i, j, mappedRowIndex, mappedColumnIndex)

            self.DisplayImage(self.transformedImageFigure)
        except: self.ShowErrorMessage("Something Wrong in Transformation Operation!      ")


    # Draw Original and/or Transformed Image on UI Canvas
    def DisplayImage(self, imageFigure):

        # Clearing canvas
        imageFigure.clear()
        imageFigure.canvas.draw()
        # Drawing subplot on canvas
        axes = imageFigure.add_subplot()
        axes.set_ylim(186, 0)
        axes.set_xlim(0, 186)
        axes.xaxis.set_ticks_position('top')
        axes.xaxis.set_ticks(np.arange(0, 186, 30))
        axes.yaxis.set_ticks(np.arange(0, 186, 30))
        imageCanvas = FigureCanvas(imageFigure)
        # Displaying image, whether original or transformed, on canvas
        if imageFigure == self.originalImageFigure:
            self.ui.originalImageGridLayout.addWidget(imageCanvas, 0, 0, 1, 1)
            axes.imshow(self.originalImage, cmap="gray" , origin='upper')
        elif imageFigure == self.transformedImageFigure:
            self.ui.transformedImageGridLayout.addWidget(imageCanvas, 0, 0, 1, 1)
            axes.imshow(self.transformedImage, cmap="gray" , origin='upper')


                                                                # # # # # # # # # # Helper Functions # # # # # # # # # #


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