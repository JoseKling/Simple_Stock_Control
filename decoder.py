#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  4 16:05:54 2021

@author: kling
"""


#%% Import packages

import numpy as np

#%% Funcitons

def decoder(line):
    #Gets only the part of the line where the barcode is
    pixels, check = get_code_pixels(line)
    if not check:
        return(0, False)
    #Gets the ammount of pixels in each of the modules
    n_pixels = get_n_pixels(pixels)
    #Constructs a prototype of the classes
    prototypes = get_prototypes(n_pixels)
    #Gets the left and right parts of the barcode, with the ammont of pixels
    #each of the modules
    codes = get_digit_codes(n_pixels)
    #Gets the similarity of each of the codes read to the prototypes
    prob = get_probabilities(codes, prototypes)
    #Now we must try the most probable first, until we get a valid code
    return(get_result(prob, prototypes))
    
def get_code_pixels(line):
    center = int(len(line)/2)
    #These modifications guarantee that the beggining and end parts of the 
    #image are not constant
    line[0] = 1
    line[1] = 0
    line[-1] = 0
    line[-1] = 1
    changes = np.zeros_like(line)
    changes[1:] = line[1:] - line[:-1]
    #Index of the pixel to the left ot the next black bar (a white pixel)
    l_index = np.argmin(changes[center:]) + center -1
    #Index of the pixel to the right ot the next black bar (also a white pixel)
    r_index = np.argmax(changes[l_index:]) + l_index
    #Keeps track of how many pairs we added. There are a total of 30 pairs.
    for n_pairs in range(29):
        #This gets the position of the white pixel
        temp = changes[:l_index]
        if len(temp) == 0 or len(changes[r_index+1:]) == 0:
            return(0, False)
        l_next = np.argmin(temp[::-1])+2
        r_next = np.argmax(changes[r_index+1:])+1
        #To guarantee that we will not scan something outside of the barcode,
        #we compare the width of the pairs in each side and choose the smallest
        if l_next < r_next:
            l_index = l_index - l_next
        else:
            r_index = r_index + r_next
    return(line[l_index+1:r_index], True)
    
def get_n_pixels(pixels):
    '''
    Gets the numbers of pixels in each of the modules. 
    '''
    count_pixels = 1
    last_pixel = 0
    index = 0
    n_pixels = np.zeros(59)
    for pixel in pixels[1:]:
        if pixel == last_pixel:
            count_pixels += 1
        else:
            last_pixel = pixel
            n_pixels[index] = count_pixels
            index += 1
            count_pixels = 1
    n_pixels[58] = count_pixels
    return(n_pixels)

def get_prototypes(n_pixels):
    #Average width of a single black bar
    black_indexes = np.array([0,2,28,30,-3,-1], int)
    black_width = np.mean(n_pixels[black_indexes])
    #Average width of a single white bar
    white_indexes = np.array([1,27,29,31,-2], int)
    white_width = np.mean(n_pixels[white_indexes])
    #There are the codes used by the EAN-13 standard. It represents the width
    #of each bar composing the digits
    even_codes = np.array([[3,2,1,1], [2,2,2,1], [2,1,2,2], [1,4,1,1],
                        [1,1,3,2], [1,2,3,1], [1,1,1,4], [1,3,1,2],
                        [1,2,1,3], [3,1,1,2]], float)
    #Get the prototypes for the even codes
    even_prototypes = np.zeros_like(even_codes)
    even_prototypes[:,[0,2]] = even_codes[:,[0,2]]*white_width 
    even_prototypes[:,[1,3]] = even_codes[:,[1,3]]*black_width
    #Get the prototypes for the odd codes
    odd_prototypes = even_codes[:,::-1]
    odd_prototypes[:,[0,2]] = odd_prototypes[:,[0,2]]*white_width 
    odd_prototypes[:,[1,3]] = odd_prototypes[:,[1,3]]*black_width
    return(np.array([*even_prototypes, *odd_prototypes]))
    
def get_digit_codes(n_pixels):
    codes = []
    start = 3
    #Get the codes on the left part
    for i in range(6):
        code = n_pixels[start:start+4]
        codes.append(code)
        start = start+4
    start = 32
    #Gets the codes on the right part
    for i in range(6):
        code = n_pixels[start:start+4]
        codes.append(code)
        start = start+4
    return(codes)

def get_probabilities(codes, prototypes):
    #Gets the squared euclidean distance of each code to each of the 
    #prototypes as points in the 4 dimensional space.
    #The matrix dists is 12x20. The position (i,j) corresponding to the
    #distance from code i to the prototype j.
    dists = np.array([[np.sum((code-prototype)**2) 
                       for prototype in prototypes] 
                       for code in codes])
    #Gets the maximum distance of each code to one of the prototypes
    max_dists = np.max(dists, axis=1)
    #Gets the probabilities for each code being a particular prototype
    prob = np.zeros_like(dists)
    for i in range(12):
        for j in range(20):
            prob[i,j] = 1-(dists[i,j]/max_dists[i])
        #Normalizes the probabilities
        prob[i,:] = prob[i,:]/np.sum(prob[i,:])
    return(prob)

def get_result(prob, prototypes):
    #Get the guess with the highest probability
    best_indexes = np.argmax(prob, axis=1)
    indexes = best_indexes.copy()
    guess = np.array([indexes%10, indexes//10], int)
    code, check = check_guess(guess, prototypes)
    #If it passes the tests, return it.
    if check:
        return(code, check) 
    #Turns the probabilities for each line upside down, then shifts it so the
    #maximum (now minimum) is equal to zero, and then sets this entry to 1.
    #Now the second highest value of the line is the minimum.
    temp = prob.copy()
    temp = -1*temp
    for i in range(12):
        
        temp[i,:] = temp[i,:] - temp[i, indexes[i]]
        temp[i, indexes[i]] = 1
    #We will scan for the best 10 guesses. If the code is not one of the best
    #12, then we assume we could not find it.
    for _ in range(12):
        best_guesses = np.argmin(prob, axis=1)
        prob_diffs = [temp[i, indexes[i]] for i in range(12)]
        new_index = np.argmin(prob_diffs)
        indexes[new_index] = best_guesses[new_index]
        guess = np.array([indexes%10, indexes//10], int)
        code, check = check_guess(guess, prototypes)
        if check:
            return(code, check)
        temp[new_index, indexes[new_index]] = 1
        indexes = best_indexes
    return(code, False)

def check_guess(guess, prototypes):
    code = np.zeros(13, int)
    first_digit_codes = [[0,0,0,0,0,0], [0,0,1,0,1,1], [0,0,1,1,0,1],
                         [0,0,1,1,1,0], [0,1,0,0,1,1], [0,1,1,0,0,1],
                         [0,1,1,1,0,0], [0,1,0,1,0,1], [0,1,0,1,1,0],
                         [0,1,1,0,1,0]]
    #If the first number is from the odd alphabet the code is upside down
    if guess[1,0] == 1:
        guess = guess[:,::-1]
        guess[1,:] = (guess[1,:]+1)%2
    #Now we get the first digit, wich is determined by the parity of the 
    #numbers onthe left of the code
    first_digit = np.where((first_digit_codes==guess[1,:6]).all(axis=1))
    first_digit = first_digit[0]
    #If we could not a matching code, then this is not a valid guess
    if len(first_digit) == 0:
        return(code, False)
    first_digit = int(first_digit[0])
    guess = guess[0,:]
    #The last checking mechanism is the checksum digit. The last number must
    #match the calculation of the checksum.
    checksum = (np.sum(guess[:-1:2])*3+np.sum(guess[1:-1:2])+first_digit)
    checksum = 10-(checksum%10)
    if checksum != guess[-1]:
        return(code, False)
    code[0] = first_digit
    code[1:] = guess
    return(code, True)