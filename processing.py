#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 10 09:01:20 2021

@author: kling
"""
#%% Packages

import numpy as np

#%% Functions

def processing(line):
    #Normalize de image
    line = line/255   
             
  #It seems that this smoothing is hurting the detection of the lines. Also,
  #there is no mention of what the method for the smoothing is, so for now
  #we won't use any.
  
    ##Convolution with a Gaussian kernel to smooth the line
    #std = 1
    #kernel = [ 1/(np.exp((i*i)/(2*std*std)*np.sqrt(2*np.pi*std))) 
    #              for i in range(-2,3)]
    #kernel = kernel/np.sum(kernel)
    #for i in range(3):
    #    line[:,i] = np.convolve(line[:,i], kernel, 'same')
 
    #Calculate the luminance of the line
    line = np.array([0.114*pixel[0] + 0.587*pixel[1] + 0.299*pixel[2]
                     for pixel in line])
    #Get maxima and minima with difference of at least delta
    max_min = get_max_min(line)
    #Prune high minima and low maxima
    max_min = prune(line, max_min)
    thresh = get_thresh(line, max_min)
    line = (line >= thresh)
    return(line.astype(int))
    
def get_max_min(line):
        delta = 0.01
        max_min = [0]
        last_index = 0
        if line[1] > line[0]:
            last_max = False
        else:
            last_max = True
        #Sets max_min to -1 for minima and to 1 for maxima
        for index in range(1, len(line)-1):
            #Found a minimum
            if (line[index-1] >= line[index] and
                line[index+1] > line[index]):
                #If the last value found was also a minimum and this one is
                #lower, then erase the last and keep this
                if last_max == False and line[last_index] > line[index]:
                    max_min.pop(-1)
                    max_min.append(-index)
                    last_index = -index
                #If the last value found was a maximum and this value found is
                #below the previous value minus delta, then keep it.
                elif last_max and line[index] < line[last_index] - delta:
                    max_min.append(-index)
                    last_max = False
                    last_index = -index
            #Found a maximum
            elif (line[index-1] <= line[index] and
                line[index+1] < line[index]):
                #If the last value found was also a maximum and this one is
                #higher, then erase the last and keep this
                if last_max == True and line[last_index] < line[index]:
                    max_min.pop(-1)
                    max_min.append(index)
                    last_index = index
                #If the last value found was a minimum and this value found is
                #above the previous value plus delta, then keep it.
                elif last_max == False and line[index] > line[last_index] + delta:
                    max_min.append(index)
                    last_max = True
                    last_index = index
        if line[-1] > line[-2]:
            max_min.append(len(line)-1)
        else:
            max_min.append(-1*(len(line)-1))
        return(np.array(max_min, int))
    
def prune(line, max_min):
    #Gets the average value of the maxima
    avg_max = np.mean(line[max_min[max_min > 0]])
    #Gets the average value of the minima
    avg_min = np.mean(line[-1*max_min[max_min < 0]])
    #Erases the maxima that are smaller the the average of the minima and the
    #minima that are higher than the average of the maxima
    new_max_min = []
    for value in max_min:
        if value > 0 and line[value] >= avg_min:
            new_max_min.append(value)
        elif value < 0 and line[-value] <= avg_max:
            new_max_min.append(value)
    return(np.array(new_max_min))

def get_thresh(line, max_min):
    center = int(len(line)/2)
    r_index = np.where(np.abs(max_min) > center)[0][0]
    l_index = np.where(np.abs(max_min) < center)[0][-1]
    thresh = np.zeros_like(line)
    
    index = 0
    while r_index < len(max_min):
        last_7 = max_min[r_index-7: r_index]
        avg_max = np.mean(line[last_7[last_7>0]])
        avg_min = np.mean(line[-1*last_7[last_7<0]])
        thresh[center + index] = np.nanmean([avg_max, avg_min])
        if index + center == np.abs(max_min[r_index]):
            r_index += 1
        index += 1
        
    index = 0
    while l_index >= 0:
        next_7 = max_min[l_index+1: l_index+8]
        avg_max = np.mean(line[next_7[next_7>0]])
        avg_min = np.mean(line[-1*next_7[next_7<0]])
        thresh[center - index] = np.nanmean([avg_max, avg_min])
        if center - index == np.abs(max_min[l_index]):
            l_index -= 1
        index += 1
    return(thresh)