#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 14 12:20:05 2018

@author: radiation
"""
import numpy as np
import random
import configparser
import math
from help_functions import load_hdf5
from help_functions import visualize
from help_functions import group_images


#for training process
def get_data_training(hdf5_train_imgs, hdf5_train_groundTruth, patch_height, patch_width,
                      N_subimgs):
    train_imgs_original = load_hdf5(hdf5_train_imgs)
    
    train_masks = load_hdf5(hdf5_train_groundTruth)
    
    
#    train_imgs = preprocessing(train_imgs_original)
    train_imgs = train_imgs_original
    #extract Training patches from the full images
    
    patches_imgs_train, patches_masks_train = extract_random(train_imgs,train_masks,patch_height,patch_width,N_subimgs)
    
    return patches_imgs_train,patches_masks_train


#for testing process
def get_data_predict(predict_imgs, predict_groundTruth, patch_height,patch_width):
    pass

#for prepare dataset
def extract_ordered(full_imgs, patch_h, patch_w):
    '''
    extract patches for image, the mask along with patches
    '''
    pass

def preprocessing(imgs_original):
    '''
    preprocess the image using the method in the paper
    imgs_original: N_imgs * height * width * channel
    
    return: N_imgs * height * width * channel
    '''
    #optical_den = -math.log10(imgs_original / 255)
    pass

def extract_random(full_imgs,full_masks, patch_h,patch_w, N_patches):
    if N_patches % full_imgs.shape[0] != 0:
        print("please enter a multiple of 24")
        exit()
       
    #check the data consistancy
    assert (len(full_imgs.shape)==4 and len(full_masks.shape)==4)  #4D arrays
    assert (full_imgs.shape[1]==1 or full_imgs.shape[1]==3)  #check the channel is 1 or 3
    assert (full_masks.shape[1]==1)   #masks only black and white
    assert (full_imgs.shape[2] == full_masks.shape[2] and full_imgs.shape[3] == full_masks.shape[3])
    
    #channel * height * width
    patches = np.empty((N_patches,full_imgs.shape[1],patch_h,patch_w))
    patches_masks = np.empty((N_patches,full_masks.shape[1],patch_h,patch_w))
    
    img_h = full_imgs.shape[2]  #height of the full image
    img_w = full_imgs.shape[3] #width of the full image
    
    patch_per_img = int(N_patches/full_imgs.shape[0])
    
    iter_tot = 0
    
    patch_per_class = patch_per_img / 3
    for i in range(full_imgs.shape[0]):
        k = 0
        counter = {0:0,1:0,2:0}
        
        while k < patch_per_img:
            
            x_center = random.randint(0+int(patch_w/2),img_w - int(patch_w/2) - 1)
            
            y_center = random.randint(0+int(patch_h/2),img_h - int(patch_h/2) - 1)

            if counter[full_masks[i,0,y_center,x_center]] < patch_per_class:
#                print("image:{}, {} class has: {}".format(i,full_masks[i,0,y_center,x_center],counter[full_masks[i,0,y_center,x_center]]))
                patch_img = full_imgs[i,:,y_center - int(patch_h/2):y_center + int(patch_h/2)+1,x_center - int(patch_w/2):x_center + int(patch_w/2) + 1]
                patch_mask = full_masks[i,:,y_center - int(patch_h/2):y_center + int(patch_h/2)+1,x_center - int(patch_w/2):x_center + int(patch_w/2)+1]
                
                patches[iter_tot] = patch_img
                patches_masks[iter_tot] = patch_mask
                
                counter[full_masks[i,0,y_center,x_center]] += 1
                iter_tot += 1
                k += 1
    
    return patches, patches_masks
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    