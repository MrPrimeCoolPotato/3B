from OAKWrapper import *
import cv2
import IMPP
import numpy as np
#f#rom mathForCord import *
import time

def CalcX(x, y):
    a = 0.0124
    b = 0.4465
    c = 207.5664

    xCord = (a*x)+(b*y)+c
    return xCord




def CalcY(x, y):

    a = 0.4664
    b = -0.0095
    c = -242.5289

    yCord = (a*x)+(b*y)+c
    return yCord




def pipeLine(cam, findObject, controlObject):
    #Inputs 
     #standart cut

    frame = cam.getFrame()
    cut1 = frame[72:722, 327:1228]
    cut2 = frame[424:532, 492:705]

    #Pipeline, Billed behandling 
    pipeline = IMPP.PostProcessingPipeline([ IMPP.AverageBlur(7),
                                        IMPP.ConvertRGB2HSV(),                                    
                                        IMPP.HSVThreshold(lowerBound=np.array([24, 146, 0]), upperBound=np.array([43, 255, 135]), outputMask=True, invert= True),
                                        IMPP.Dilate(3,3),
                                        IMPP.Erode(3,3),
                                        IMPP.DetectContours(mode=cv2.RETR_LIST),
                                        IMPP.DetectShapes(epsilon= 0.1, printResult=False)
                                        ])
    
    pipelineOutput1 = pipeline.run(cut1)
    pipelineOutput2 = pipeline.run(cut2)
       
    cv2.imshow("billed", cut1)

    #Fejlhåndtering
    if findObject:
        firstShape = pipelineOutput1[0] 
        
        #Beregn arealet af det første objekt
        Area = cv2.contourArea(firstShape.contour)
       
        myRotatedRect = cv2.minAreaRect(firstShape.contour)

        Orientation = myRotatedRect[2]
        if myRotatedRect[0] < myRotatedRect[1]:
             Orientation = Orientation - 90
    
        
        #Beregn Robot koordinater ud fra Billed koordinater
        print('FIRSTSHAPE: ', firstShape.center)
        y = CalcY(firstShape.center[0], firstShape.center[1])
        x = CalcX(firstShape.center[0], firstShape.center[1])
        Area2=1
    elif len(pipelineOutput1) == None:
        Area=1
        x=0
        y=0
        Orientation=0
        Area2=1
        raise ValueError("No object")



    if controlObject:
        controlShape = pipelineOutput2[0] 
        #Beregn arealet af det kontrol objekt
        Area2 = cv2.contourArea(controlShape.contour)
        x=0
        y=0
        Orientation=0
        Area=1

    elif len(pipelineOutput2) == None:
        Area2=1
        Area=1
        x=0
        y=0
        Orientation=0
        Area2=1
        raise ValueError("No object")

    
    cv2.waitKey(1)

    #return [0,     1,               2,          3,            4]
    return [int(x), int(y), int(Orientation), int(Area), int(Area2)]
    

