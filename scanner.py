#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  5 16:54:23 2021

@author: kling

Article: Robust Recognition of 1-D Barcodes Using Camera Phones
Authors: Steffen Wachenfeld, Sebastian Terlunen, Xiaoyi Jiang
Link: https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.214.5089&rep=rep1&type=pdf
"""

#%% Packages

import numpy as np
import cv2 as cv
from decoder import decoder
from processing import processing

#%% Functions

def scanner():
    code = np.zeros(12)
    url = 'http://192.168.42.129:8080/video'
    cap = cv.VideoCapture(url)
    ret, frame = cap.read()
    y_center = int(frame.shape[0]/2)
    x_center = int(frame.shape[1]/2)
    display_message = False
    check = False
    while not check:
        while True:
            ret, frame = cap.read()
            if not ret:
                raise Exception('Could not read video.')
            img = frame
            line = img[y_center,:].copy()
            cv.circle(img, (x_center, y_center), 10, (0,255,0), -1)
            cv.circle(img, (x_center, y_center), 10, (0,0,255), 1)
            cv.putText(img, 'Press enter to scan. Press esc to exit.',
                       (0, 30), cv.FONT_HERSHEY_SIMPLEX, 1, (0,0,255))
            if display_message:
                cv.putText(img, 'Could not scan. Please try again.',
                       (0, 60), cv.FONT_HERSHEY_SIMPLEX, 1, (0,0,255))
            img[y_center,:,:] = [0,0,255]
            cv.imshow('Scan', img)
            k = cv.waitKey(1)
            if k == 27:
                cap.release()
                cv.destroyAllWindows()
                exit()
            elif k == 13:
                break
        code, check = decoder(processing(line))
        if not check:
            display_message = True
    cap.release()
    cv.destroyAllWindows()
    return(code)
        
if __name__ == '__main__':
    print(*scanner())
