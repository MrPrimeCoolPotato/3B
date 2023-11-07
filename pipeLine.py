from OAKWrapper import *
import cv2
import IMPP
import numpy as np
from mathForCord import *

#Inputs 
cam = OAKCamColorDepth()
frame = cam.getFrame()
cut = frame[72:722, 327:1228]


#Pipeline, Billed behandling 
pipeline = IMPP.PostProcessingPipeline([IMPP.ConvertRGB2HSV(),
                                        IMPP.HSVThreshold(lowerBound=np.array([0, 0, 0]), upperBound=np.array([64, 255, 253]), outputMask=True),
                                        IMPP.DetectContours(mode=cv2.RETR_LIST, draw=False),
                                        IMPP.DetectShapes(printResult=True)
                                        ])

pipelineOutput = pipeline.run(cut)

#Fejlhåndtering
if len(pipelineOutput) == 0:
    raise ValueError("No object")

firstShape = pipelineOutput[0] 

#Beregn arealet af det første objekt
Area = cv2.contourArea(firstShape.contour)
Orientation = cv2.minAreaRect(firstShape.contour)

#Beregn Robot koordinater ud fra Billed koordinater
y = CalcY(firstShape.center[0], firstShape.center[1])
x = CalcX(firstShape.center[0], firstShape.center[1])

#Output from Pipeline
def Output():
    return [x, y, Orientation, Area]
    

'''if input() == 'debug':
    #Debug
    print("x", x, "y", y)

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
    
    if cv2.waitKey(0) == ord('q'):
        cv2.destroyAllWindows()
   ''' 



