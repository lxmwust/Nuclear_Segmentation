#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 14 12:29:38 2018

@author: radiation
"""
import h5py
from PIL import Image
import numpy as np


def load_hdf5(infile):
  with h5py.File(infile,"r") as f:  #"with" close the file after its nested commands
    return f["image"][()]

def write_hdf5(arr,outfile):
  with h5py.File(outfile,"w") as f:
    f.create_dataset("image", data=arr, dtype=arr.dtype)
    
def pred_to_imgs():
    pass

#visualize image (as PIL image)
def visualize(data,filename):
    assert (len(data.shape)==3) #height*width*channels
    img = None
    if data.shape[2]==1:  #in case it is black and white
        data = np.reshape(data,(data.shape[0],data.shape[1]))
    if np.max(data)>1:
        img = Image.fromarray(data.astype(np.uint8))   #the image is already 0-255
    else:
        img = Image.fromarray((data*255).astype(np.uint8))  #the image is between 0-1
    img.save(filename + '.png')
    return img

def group_images(data,per_row):
    assert data.shape[0]% per_row == 0
    
    assert (data.shape[1]==1 or data.shape[1]==3)
    data = np.transpose(data,(0,2,3,1))  #corect format for imshow
    all_stripe = []
    for i in range(int(data.shape[0]/per_row)):
        stripe = data[i*per_row]
        for k in range(i*per_row+1, i*per_row+per_row):
            stripe = np.concatenate((stripe,data[k]),axis=1)
        all_stripe.append(stripe)
    
    totimg = all_stripe[0]
    for i in range(1,len(all_stripe)):
        totimg = np.concatenate((totimg,all_stripe[i]),axis=0)
    return totimg

def parse_mask(masks):
    assert(len(masks.shape)==4)
    
    inside_masks = np.empty(masks.shape)
    boundary_masks = np.empty(masks.shape)
    for index in range(masks.shape[0]):
        inside_mask = masks[index].copy()
        inside_mask[masks[index] == 2] = 0
        inside_masks[index] = inside_mask
        boundary_mask = masks[index].copy()
        boundary_mask[masks[index]==1] = 0
        boundary_mask[masks[index]==2] = 1
        boundary_masks[index] = boundary_mask

    return inside_masks, boundary_masks

def masks_nucleiNet(masks):
    assert (len(masks.shape)==4)  #4D arrays
    assert (masks.shape[1]==1 )  #check the channel is 1
    im_h = masks.shape[2]
    im_w = masks.shape[3]
    new_masks = np.empty((masks.shape[0],3))
    for i in range(masks.shape[0]):
            if  masks[i,0,int(im_h/2),int(im_w/2)] == 0:
                new_masks[i,0]=1
                new_masks[i,1]=0
                new_masks[i,2]=0
            elif masks[i,0,int(im_h/2),int(im_w/2)] == 1:
                new_masks[i,0]=0
                new_masks[i,1]=1
                new_masks[i,2]=0
                
            else:
                new_masks[i,0]=0
                new_masks[i,1]=0
                new_masks[i,2]=1
    return new_masks

#determine the distribution of class 
def class_distribution_train(ground_truth):

    assert(len(ground_truth.shape) == 2)
    positive = {0:0,1:0,2:0}
    for index in range(len(ground_truth)):
        if (ground_truth[index] == np.array([1,0,0])).all():
            positive[0] += 1
        elif (ground_truth[index] == np.array([0,1,0])).all(): 
            positive[1] += 1
        else:
            positive[2] += 1

    for key in positive.keys():
        print("Percent of {} in dataset: {} ".format(str(key),str(positive[key]/len(ground_truth))))

        
        
def pred_to_imgs(pred, patch_height, patch_width, mode="original"):
    assert (len(pred.shape)==3)  #3D array: (Npatches,height*width,2)
    assert (pred.shape[2]==2 )  #check the classes are 2
    pred_images = np.empty((pred.shape[0],pred.shape[1]))  #(Npatches,height*width)
    if mode=="original":
        for i in range(pred.shape[0]):
            for pix in range(pred.shape[1]):
                pred_images[i,pix]=pred[i,pix,1]
    elif mode=="threshold":
        for i in range(pred.shape[0]):
            for pix in range(pred.shape[1]):
                if pred[i,pix,1]>=0.5:
                    pred_images[i,pix]=1
                else:
                    pred_images[i,pix]=0
    else:
        print("mode " +str(mode) +" not recognized, it can be 'original' or 'threshold'")
        exit()
    pred_images = np.reshape(pred_images,(pred_images.shape[0],1, patch_height, patch_width))
    return pred_images