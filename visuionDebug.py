from OAKWrapper import *
import cv2
import IMPP
import numpy as np

Icam = OAKCamColorDepth()

pipeline = IMPP.PostProcessingPipeline([ IMPP.AverageBlur(7),
                                        IMPP.ConvertRGB2HSV(),                                    
                                        IMPP.HSVThreshold(lowerBound=np.array([24, 146, 0]), upperBound=np.array([43, 255, 135]), outputMask=True, invert= True, showOutput=True),
                                        IMPP.Dilate(3,3),
                                        IMPP.Erode(3,3),
                                        IMPP.DetectContours(mode=cv2.RETR_LIST, draw=True),
                                        IMPP.DetectShapes(epsilon= 0.1, printResult=True)
                                        ])

while True:
    frame = Icam.getFrame()
    cut = frame[424:532, 492:705]
    cv2.imshow("billed", cut)


    pipelineOutput = pipeline.run(cut)
    controlShape = pipelineOutput[0]
    print("areal: ", cv2.contourArea(controlShape.contour))
        
    shapeImg = cut.copy() 
    for shape in pipelineOutput: 
        cv2.drawContours(shapeImg , [shape.contour], -1, (0, 255, 0), 2) 
        cv2.putText(shapeImg, str(shape.points), shape.center, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 255, 2)
        shape1Area = cv2.minAreaRect(shape.contour)
        #cv2.drawContours(shapeImg, [shape1Area], -1, (0, 255, 0), 2)
        box = cv2.boxPoints(shape1Area)
        box = np.int0(box)
        cv2.drawContours(shapeImg, [box], 0, (0,0,255),2)
        

    cv2.imshow('drawn', shapeImg)

    if cv2.waitKey(1) == ord("q"):
        cv2.imwrite("cut2.png", shapeImg)
        cv2.destroyAllWindows()
        break