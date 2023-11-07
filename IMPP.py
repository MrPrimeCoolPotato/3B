# By Mathias Gregersen, megr@ucl.dk
# Version 0.3
import numpy as np
import cv2
#from numpy.lib.function_base import percentile
import imutils

#print('Importing IMPP')

# Pipeline
class PostProcessingPipeline:
    def __init__(self, blocks) -> None:
        if type(blocks) != list:
            raise Exception('First input should be of type list, this is currently type: ' + str(type(blocks)))
        self.blocks = blocks

    def run(self, input):
        output = input
        for block in self.blocks:
            if not isinstance(block, PostProcessingBlock):
                raise Exception('Processing block is not a subclass of ' + str(PostProcessingBlock) + ' it is currently type: ' + str(type(block)))
            output = block.run(output)
        return output


# Generics
class PostProcessingBlock:
    def run(self, input):
        return input

class CustomKernel(PostProcessingBlock):
    def __init__(self, kernel, showOutput = False, outputWindowName = 'CustomKernel') -> None:
        self.kernel = kernel
        self.showOutput = showOutput
        self.outputWindowName = outputWindowName

    def run(self, input):
        output = cv2.filter2D(input, -1, self.kernel)
        if self.showOutput:
            cv2.imshow(self.outputWindowName, output)
        return output


# Conversions
class ConvertGeneric(PostProcessingBlock):
    def __init__(self, code: int = cv2.COLOR_BGR2GRAY, showOutput = False, outputWindowName = 'ConvertGeneric') -> None:
        self.showOutput = showOutput
        self.outputWindowName = outputWindowName
        self.code = code

    def run(self, input):
        output = cv2.cvtColor(input, self.code)
        if self.showOutput:
            cv2.imshow(self.outputWindowName, output)
        return output

class ConvertBGR2Gray(ConvertGeneric):
    def __init__(self, showOutput=False, outputWindowName='ConvertBGR2Gray') -> None:
        super().__init__(code=cv2.COLOR_BGR2GRAY, showOutput=showOutput, outputWindowName=outputWindowName)

class ConvertBGR2HSV(ConvertGeneric):
    def __init__(self, showOutput=False, outputWindowName='ConvertBGR2HSV') -> None:
        super().__init__(code=cv2.COLOR_BGR2HSV, showOutput=showOutput, outputWindowName=outputWindowName)

class ConvertRGB2HSV(ConvertGeneric):
    def __init__(self, showOutput=False, outputWindowName='ConvertRGB2HSV') -> None:
        super().__init__(code=cv2.COLOR_RGB2HSV, showOutput=showOutput, outputWindowName=outputWindowName)

class ConvertHSV2BGR(ConvertGeneric):
    def __init__(self, showOutput=False, outputWindowName='ConvertHSV2BGR') -> None:
        super().__init__(code=cv2.COLOR_HSV2BGR, showOutput=showOutput, outputWindowName=outputWindowName)

class ConvertHSV2RGB(ConvertGeneric):
    def __init__(self, showOutput=False, outputWindowName='ConvertHSV2RGB') -> None:
        super().__init__(code=cv2.COLOR_HSV2RGB, showOutput=showOutput, outputWindowName=outputWindowName)

class ConvertToGray(PostProcessingBlock): # Deprecated
    def __init__(self, showOutput = False, outputWindowName = 'Grayscale') -> None:
        self.showOutput = showOutput
        self.outputWindowName = outputWindowName

    def run(self, input):
        gray = cv2.cvtColor(input, cv2.COLOR_BGR2GRAY)

        if self.showOutput:
            cv2.imshow(self.outputWindowName, gray)

        return gray

class GetRedChannel(PostProcessingBlock):
    def __init__(self, showOutput = False, outputWindowName = 'RedChannel') -> None:
        self.showOutput = showOutput
        self.outputWindowName = outputWindowName
        self.grayscale = ConvertToGray()

    def run(self, input):
        output = input.copy()
        output[:, :, 0] = 0
        output[:, :, 1] = 0
        output = self.grayscale.run(output)
        if self.showOutput:
            cv2.imshow(self.outputWindowName, output)
        return output

class GetGreenChannel(PostProcessingBlock):
    def __init__(self, showOutput = False, outputWindowName = 'GreenChannel') -> None:
        self.showOutput = showOutput
        self.outputWindowName = outputWindowName
        self.grayscale = ConvertToGray()

    def run(self, input):
        output = input.copy()
        output[:, :, 0] = 0
        output[:, :, 2] = 0
        output = self.grayscale.run(output)
        if self.showOutput:
            cv2.imshow(self.outputWindowName, output)
        return output

class GetBlueChannel(PostProcessingBlock):
    def __init__(self, showOutput = False, outputWindowName = 'BlueChannel') -> None:
        self.showOutput = showOutput
        self.outputWindowName = outputWindowName
        self.grayscale = ConvertToGray()

    def run(self, input):
        output = input.copy()
        output[:, :, 1] = 0
        output[:, :, 2] = 0
        output = self.grayscale.run(output)
        if self.showOutput:
            cv2.imshow(self.outputWindowName, output)
        return output
        

# Intensity transformation
class IntensityPower(PostProcessingBlock):
    def __init__(self, power: float, showOutput = False, outputWindowName = 'IntensityPower') -> None:
        self.power = power
        self.showOutput = showOutput
        self.outputWindowName = outputWindowName

    def run(self, input):
        output = input.copy()
        output = np.array(255*(output / 255) ** self.power, dtype = 'uint8')
        if self.showOutput:
            cv2.imshow(self.outputWindowName, output)
        return output


# Blurring
class AverageBlur(CustomKernel):
    def __init__(self, filterSize, trackbar: bool = False, trackbarStart: int = 0, trackMax: int = 99, trackbarName: str = "Average Blur Trackbar", showOutput = False, outputWindowName = 'AverageBlur') -> None:
        self.kernel = np.ones((filterSize,filterSize), np.float32)/(filterSize*filterSize)
        self.showOutput = showOutput
        self.outputWindowName = outputWindowName
        self.trackMax = trackMax
        if trackbar:
            self.createTrackbar(trackbarStart, trackbarName)

    def createTrackbar(self, startVal, trackbarName):
        cv2.namedWindow(trackbarName)
        cv2.createTrackbar("Filter Size", trackbarName, startVal, self.trackMax, self.setFilterSize)

    def setFilterSize(self, value: int):
        if value < 1 or value > self.trackMax:
            return
        if value % 2 == 0:
            value = value - 1
        self.kernel = np.ones((value,value), np.float32)/(value*value)

class GaussianBlur(CustomKernel):
    def __init__(self, filterSize, trackbar: bool = False, trackbarStart: int = 0, trackMax: int = 99, trackbarName: str = "Gaussian Blur Trackbar", showOutput = False, outputWindowName = 'GaussianBlur') -> None:
        self.kernel = cv2.getGaussianKernel(filterSize, cv2.CV_32F)
        self.showOutput = showOutput
        self.outputWindowName = outputWindowName
        self.trackMax = trackMax
        if trackbar:
            self.createTrackbar(trackbarStart, trackbarName)

    def createTrackbar(self, startVal, trackbarName):
        cv2.namedWindow(trackbarName)
        cv2.createTrackbar("Filter Size", trackbarName, startVal, self.trackMax, self.setFilterSize)

    def setFilterSize(self, value: int):
        if value < 1 or value > self.trackMax:
            return
        if value % 2 == 0:
            value = value - 1
        self.kernel = cv2.getGaussianKernel(value, cv2.CV_32F)

class MedianBlur(PostProcessingBlock):
    def __init__(self, filterSize, trackbar: bool = False, trackbarStart: int = 0, trackMax: int = 99, trackbarName: str = "Median Blur Trackbars", showOutput = False, outputWindowName = 'MedianBlur') -> None:
        self.filterSize = filterSize
        self.showOutput = showOutput
        self.outputWindowName = outputWindowName
        self.trackMax = trackMax
        if trackbar:
            self.createTrackbar(trackbarStart, trackbarName)

    def run(self, input):
        output = cv2.medianBlur(input, self.filterSize)
        if self.showOutput:
            cv2.imshow(self.outputWindowName, output)
        return output

    def createTrackbar(self, startVal, trackbarName):
        cv2.namedWindow(trackbarName)
        cv2.createTrackbar("Filter Size", trackbarName, startVal, self.trackMax, self.setFilterSize)

    def setFilterSize(self, value: int):
        if value < 1 or value > self.trackMax:
            return
        if value % 2 == 0:
            value = value - 1
        self.filterSize = value

class BilateralFilter(PostProcessingBlock):
    def __init__(self, filterSize, sigmaColor, sigmaSpace, showOutput = False, outputWindowName = 'BilateralFilter') -> None:
        self.filterSize = filterSize
        self.sigmaColor = sigmaColor
        self.sigmaSpace = sigmaSpace
        self.showOutput = showOutput
        self.outputWindowName = outputWindowName

    def run(self, input):
        output = cv2.bilateralFilter(input, self.filterSize, self.sigmaColor, self.sigmaSpace)
        if self.showOutput:
            cv2.imshow(self.outputWindowName, output)
        return output


# Sharpening
class LaplacianSharpen(CustomKernel):
    def __init__(self, scale: float = 1, diagonal: bool = True, showOutput: bool = False, outputWindowName: str = 'LaplacianSharpen') -> None:
        if diagonal:
            iKernel = np.array([[1, 1, 1], [1, -8, 1], [1, 1, 1]], np.float32) * scale
        else:
            iKernel = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], np.float32) * scale
        super().__init__(iKernel, showOutput=showOutput, outputWindowName=outputWindowName)

    def run(self, input):
        output = cv2.filter2D(input, -1, self.kernel)
        output = cv2.add(input, output)
        if self.showOutput:
            cv2.imshow(self.outputWindowName, output)
        return output

class UnsharpMasking(PostProcessingBlock):
    def __init__(self, filterSize: int = 3, showOutput: bool = False, outputWindowName: str = 'UnsharpMasking') -> None:
        self.showOutput = showOutput
        self.outputWindowName = outputWindowName
        self.blurring = GaussianBlur(filterSize)

    def run(self, input):
        blurred = self.blurring.run(input)
        blurSub = cv2.subtract(input, blurred)
        output = cv2.add(input, blurSub)
        if self.showOutput:
            cv2.imshow(self.outputWindowName, output)
        return output


# Edges
class SobelH(CustomKernel):
    def __init__(self, showOutput=False, outputWindowName='SobelH') -> None:
        self.kernel = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], np.float32)
        self.showOutput = showOutput
        self.outputWindowName = outputWindowName

class SobelHN(CustomKernel):
    def __init__(self, showOutput=False, outputWindowName='SobelHN') -> None:
        self.kernel = np.array([[1, 0, -1], [2, 0, -2], [1, 0, -1]], np.float32)
        self.showOutput = showOutput
        self.outputWindowName = outputWindowName

class SobelV(CustomKernel):
    def __init__(self, showOutput=False, outputWindowName='SobelV') -> None:
        self.kernel = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], np.float32)
        self.showOutput = showOutput
        self.outputWindowName = outputWindowName

class SobelVN(CustomKernel):
    def __init__(self, showOutput=False, outputWindowName='SobelVN') -> None:
        self.kernel = np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]], np.float32)
        self.showOutput = showOutput
        self.outputWindowName = outputWindowName

class Sobel2(PostProcessingBlock):
    def __init__(self, showOutput=False, outputWindowName='Sobel2') -> None:
        self.showOutput = showOutput
        self.outputWindowName = outputWindowName
        self.sobelH = SobelH(showOutput)
        self.sobelV = SobelV(showOutput)

    def run(self, input):
        output = input.copy()
        frameSobelH = self.sobelH.run(output)
        frameSobelV = self.sobelV.run(output)
        output = frameSobelH + frameSobelV
        if self.showOutput:
            cv2.imshow(self.outputWindowName, output)
        return output

class Sobel4(PostProcessingBlock):
    def __init__(self, showOutput=False, outputWindowName='Sobel4') -> None:
        self.showOutput = showOutput
        self.outputWindowName = outputWindowName
        self.sobelH = SobelH(showOutput)
        self.sobelHN = SobelHN(showOutput)
        self.sobelV = SobelV(showOutput)
        self.sobelVN = SobelVN(showOutput)

    def run(self, input):
        output = input.copy()
        frameSobelH = self.sobelH.run(output)
        frameSobelHN = self.sobelHN.run(output)
        frameSobelV = self.sobelV.run(output)
        frameSobelVN = self.sobelVN.run(output)
        output = frameSobelH + frameSobelHN + frameSobelV + frameSobelVN
        if self.showOutput:
            cv2.imshow(self.outputWindowName, output)
        return output


# Thresholding (https://docs.opencv.org/4.5.2/d7/d4d/tutorial_py_thresholding.html)
class Threshold(PostProcessingBlock):
    def __init__(self, lowerBound: int, upperBound: int, mode: int = cv2.THRESH_BINARY, trackbar: bool = False, trackbarName: str = "Threshold Trackbars", showOutput: bool = False, outputWindowName: str = 'Threshold') -> None:
        self.showOutput = showOutput
        self.outputWindowName = outputWindowName
        self.lowerBound = lowerBound
        self.upperBound = upperBound
        self.mode = mode
        if trackbar:
            self.createTrackbar(trackbarName)

    def run(self, input):
        output = input.copy()
        retval, threshL = cv2.threshold(output, self.lowerBound, 255, self.mode)
        retval, threshU = cv2.threshold(output, self.upperBound, 255, self.mode)
        threshU = cv2.bitwise_not(threshU)
        output = cv2.bitwise_and(threshL, threshU)
        if self.showOutput:
            cv2.imshow(self.outputWindowName, output)
        return output

    def createTrackbar(self, trackbarName):
        cv2.namedWindow(trackbarName)
        cv2.createTrackbar("Lower Bound", trackbarName, self.lowerBound, 255, self.setLB)
        cv2.createTrackbar("Upper Bound", trackbarName, self.upperBound, 255, self.setUB)

    def setLB(self, value: int):
        if value < 0 or value > 255:
            return
        self.lowerBound = value

    def setUB(self, value: int):
        if value < 0 or value > 255:
            return
        self.upperBound = value

class HSVThreshold(PostProcessingBlock):
    def __init__(self, lowerBound: np.array = np.array([0,0,0]), upperBound: np.array = np.array([255,255,255]), invert: bool = False, outputMask: bool = False, trackbar: bool = False, trackbarName: str = "HSV Treshold Trackbars", showOutput: bool = False, outputWindowName: str = 'HSVThreshold') -> None:
        self.showOutput = showOutput
        self.outputWindowName = outputWindowName
        self.lowerBound = lowerBound
        self.upperBound = upperBound
        self.invert = invert
        self.outputMask = outputMask
        if trackbar:
            self.createTrackbar(trackbarName)

    def run(self, input):
        output = input.copy()
        mask = cv2.inRange(output, self.lowerBound, self.upperBound)
        if self.invert:
            mask = cv2.bitwise_not(mask)

        if self.outputMask:
            if self.showOutput:
                cv2.imshow(self.outputWindowName, mask)
            return mask

        output = cv2.bitwise_and(output, output, mask = mask)
        if self.showOutput:
            cv2.imshow(self.outputWindowName, output)
        return output

    def createTrackbar(self, trackbarName):
        cv2.namedWindow(trackbarName)
        cv2.createTrackbar("LBH", trackbarName, self.lowerBound[0], 255, self.setLBH)
        cv2.createTrackbar("UBH", trackbarName, self.upperBound[0], 255, self.setUBH)
        cv2.createTrackbar("LBS", trackbarName, self.lowerBound[1], 255, self.setLBS)
        cv2.createTrackbar("UBS", trackbarName, self.upperBound[1], 255, self.setUBS)
        cv2.createTrackbar("LBV", trackbarName, self.lowerBound[2], 255, self.setLBV)
        cv2.createTrackbar("UBV", trackbarName, self.upperBound[2], 255, self.setUBV)

    def setLBH(self, value: int):
        if value < 0 or value > 255:
            return
        self.lowerBound[0] = value

    def setLBS(self, value: int):
        if value < 0 or value > 255:
            return
        self.lowerBound[1] = value

    def setLBV(self, value: int):
        if value < 0 or value > 255:
            return
        self.lowerBound[2] = value

    def setUBH(self, value: int):
        if value < 0 or value > 255:
            return
        self.upperBound[0] = value

    def setUBS(self, value: int):
        if value < 0 or value > 255:
            return
        self.upperBound[1] = value

    def setUBV(self, value: int):
        if value < 0 or value > 255:
            return
        self.upperBound[2] = value

class AdaptiveThreshold(PostProcessingBlock):
    def __init__(self, upperBound: int, blockSize: int, constant: int, adaptionMode: int = cv2.ADAPTIVE_THRESH_GAUSSIAN_C, thresholdMode: int = cv2.THRESH_BINARY, showOutput: bool = False, outputWindowName: str = 'AdaptiveThreshold') -> None:
        self.showOutput = showOutput
        self.outputWindowName = outputWindowName
        self.upperBound = upperBound
        self.blockSize = blockSize
        self.constant = constant
        self.adaptionMode = adaptionMode
        self.thresholdMode = thresholdMode

    def run(self, input):
        output = cv2.adaptiveThreshold(input, self.upperBound, self.adaptionMode, self.thresholdMode, self.blockSize, self.constant)
        if self.showOutput:
            cv2.imshow(self.outputWindowName, output)
        return output

class OtsuBinarization(PostProcessingBlock):
    def __init__(self, showOutput: bool = False, outputWindowName: str = 'OtsuBinarization') -> None:
        self.showOutput = showOutput
        self.outputWindowName = outputWindowName
    
    def run(self, input):
        retval, output = cv2.threshold(input, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        if self.showOutput:
            cv2.imshow(self.outputWindowName, output)
        return output


# Contours (https://www.pyimagesearch.com/2016/02/08/opencv-shape-detection/)
class ContourDrawInfo:
    def __init__(self, color = 255, thickness: int = 1, linetype: int = 1) -> None:
        self.color = color
        self.thickness = thickness
        self.linetype = linetype

class DetectContours(PostProcessingBlock):
    def __init__(self, mode: int = cv2.RETR_EXTERNAL, method: int = cv2.CHAIN_APPROX_SIMPLE, printResult: bool = False, draw: bool = False, drawInfo: ContourDrawInfo = None, outputWindowName: str = 'DetectContours') -> None:
        self.printResult = printResult
        self.outputWindowName = outputWindowName
        self.draw = draw
        self.drawInfo = drawInfo
        self.mode = mode
        self.method = method

    def run(self, input):
        cnts = cv2.findContours(input, self.mode, self.method)
        output = imutils.grab_contours(cnts)
        if self.printResult:
            print(output)
        if self.draw:
            contoursImg = input.copy()
            contoursImg = cv2.cvtColor(contoursImg, cv2.COLOR_GRAY2BGR)
            if self.drawInfo == None:
                cv2.drawContours(contoursImg, output, -1, (0, 0, 255), 2)
                cv2.imshow(self.outputWindowName, contoursImg)
            elif isinstance(self.drawInfo, ContourDrawInfo):
                cv2.drawContours(contoursImg, output, -1, self.drawInfo.color, self.drawInfo.thickness, self.drawInfo.linetype)
                cv2.imshow(self.outputWindowName, contoursImg)
            else:
                print("Invalid drawInfo, wrong class?")
        return output

class ThresholdContours(PostProcessingBlock):
    def __init__(self, minArea: float, maxArea: float, trackbar: bool = False, trackMax: int = 10000, trackbarName: str = "HSV Treshold Trackbars", printDebug: bool = False) -> None:
        self.minArea = minArea
        self.maxArea = maxArea
        self.printDebug = printDebug
        self.trackMax = trackMax
        if trackbar:
            self.createTrackbar(trackbarName)
        
    def run(self, input):
        output = []
        for c in input:
            cArea = cv2.contourArea(c)
            if self.printDebug:
                print("Area:", cArea)
            if cArea > self.minArea and cArea < self.maxArea:
                output.append(c)
        return output

    def createTrackbar(self, trackbarName):
        cv2.namedWindow(trackbarName)
        cv2.createTrackbar("Min Area", trackbarName, self.minArea, self.trackMax, self.setMin)
        cv2.createTrackbar("Max Area", trackbarName, self.maxArea, self.trackMax, self.setMax)

    def setMin(self, value: int):
        if value < 0 or value > self.trackMax:
            return
        self.minArea = value

    def setMax(self, value: int):
        if value < 0 or value > self.trackMax:
            return
        self.maxArea = value


# Shapes (https://www.pyimagesearch.com/2016/02/08/opencv-shape-detection/)
class Shape:
    def __init__(self, perimeter, approx, center, contour) -> None:
        self.perimeter = perimeter
        self.approx = approx
        self.points = len(approx)
        self.center = center
        self.contour = contour

class DetectShapes(PostProcessingBlock):
    def __init__(self, closed: bool = True, epsilon: float = 0.04, printResult: bool = False) -> None:
        self.printResult = printResult
        self.closed = closed
        self.epsilon = epsilon

    def run(self, input):
        output = []
        for c in input:
            M = cv2.moments(c)
            if M["m00"] != 0:
                cX = int((M["m10"] / M["m00"]))
                cY = int((M["m01"] / M["m00"]))
                center = [cX, cY]
            else:
                center = None

            peri = cv2.arcLength(c, self.closed)
            approx = cv2.approxPolyDP(c, self.epsilon * peri, self.closed)
            output.append(Shape(peri, approx, center, c))

            if self.printResult:
                print("Shape: ", len(approx), peri, center)

        return output


# Morphology
class Erode(PostProcessingBlock):
    def __init__(self, size:int = 3, iterations:int = 1, trackbar:bool = False, sizeMax:int = 27, iterationsMax:int = 16, trackbarName:str = "Erode Trackbar", showOutput:bool = False, outputWindowName:str = 'Erode') -> None:
        self.showOutput = showOutput
        self.outputWindowName = outputWindowName
        self.size = size
        self.kernel = np.ones((size, size), np.uint8)
        self.iterations = iterations
        self.sizeMax = sizeMax
        self.iterationsMax = iterationsMax
        if trackbar:
            self.createTrackbar(trackbarName)

    def run(self, input):
        output = cv2.erode(input, self.kernel, iterations=self.iterations)
        if self.showOutput:
            cv2.imshow(self.outputWindowName, output)
        return output

    def createTrackbar(self, trackbarName):
        cv2.namedWindow(trackbarName)
        cv2.createTrackbar("Size", trackbarName, self.size, self.sizeMax, self.setSize)
        cv2.createTrackbar("Iterations", trackbarName, self.iterations, self.iterationsMax, self.setIterations)

    def setSize(self, value:int):
        self.size = value
        self.kernel = np.ones((self.size, self.size), np.uint8)

    def setIterations(self, value:int):
        self.iterations = value

class Dilate(PostProcessingBlock):
    def __init__(self, size:int = 3, iterations:int = 1, trackbar:bool = False, sizeMax:int = 27, iterationsMax:int = 16, trackbarName:str = "Dilate Trackbar", showOutput:bool = False, outputWindowName:str = 'Dilate') -> None:
        self.showOutput = showOutput
        self.outputWindowName = outputWindowName
        self.size = size
        self.kernel = np.ones((size, size), np.uint8)
        self.iterations = iterations
        self.sizeMax = sizeMax
        self.iterationsMax = iterationsMax
        if trackbar:
            self.createTrackbar(trackbarName)

    def run(self, input):
        output = cv2.dilate(input, self.kernel, iterations=self.iterations)
        if self.showOutput:
            cv2.imshow(self.outputWindowName, output)
        return output

    def createTrackbar(self, trackbarName):
        cv2.namedWindow(trackbarName)
        cv2.createTrackbar("Size", trackbarName, self.size, self.sizeMax, self.setSize)
        cv2.createTrackbar("Iterations", trackbarName, self.iterations, self.iterationsMax, self.setIterations)

    def setSize(self, value:int):
        self.size = value
        self.kernel = np.ones((self.size, self.size), np.uint8)

    def setIterations(self, value:int):
        self.iterations = value