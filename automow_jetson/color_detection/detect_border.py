# **********************************************************************************************
# *                                                                                            *
# *  this code references :                                                                    *
# *  https://www.geeksforgeeks.org/multiple-color-detection-in-real-time-using-python-opencv/  *
# *                                                                                            *
# **********************************************************************************************

import cv2
import numpy as np


def check(videoCaptureObject: cv2.VideoCapture):
    _, frame = videoCaptureObject.read()

    # convert from rgb to hsv colour model
    hsvFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # define mask 
    red_lower = np.array([136, 87, 111], np.uint8) 
    red_upper = np.array([180, 255, 255], np.uint8) 
    red_mask = cv2.inRange(hsvFrame, red_lower, red_upper) 

    # Morphological Transform, Dilation for each color and bitwise_and operator 
    # between imageFrame and mask determines to detect only that particular color 
    kernal = np.ones((5, 5), "uint8") 

    red_mask = cv2.dilate(red_mask, kernal) 
    res_red = cv2.bitwise_and(frame, frame, mask = red_mask) 

    contours, hierarchy = cv2.findContours(red_mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE) 

    border_detected = False

    for _, contour in enumerate(contours): 
        area = cv2.contourArea(contour)
        if(area > 1000): 
            x, y, w, h = cv2.boundingRect(contour) 
            frame = cv2.rectangle(frame, (x, y),(x + w, y + h),(0, 0, 255), 2)

            border_detected = True
            break

    # cv2.imshow("red color detection", detected_output)
    cv2.waitKey(0)

    return border_detected
