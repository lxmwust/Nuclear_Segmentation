#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 14 11:44:16 2018

@author: radiation
"""


#1.Normalize color
#2.Generate a ternary mask
#3.divide into pathces(image and mask)
#4.Save result into training,dev and test dataset


#==========================================================
#
#  This prepare the hdf5 datasets of H & E nucleui segementation
#
#============================================================

import os
import h5py
import numpy as np
from PIL import Image
import glob
import sys
sys.path.insert(0, './lib/')
from help_functions import *
import random
#save the data
def write_hdf5(arr,outfile,dataset_name):
  with h5py.File(outfile,"w") as f:
    f.create_dataset(dataset_name, data=arr, dtype=arr.dtype)

#----------------Global parameter ------------------
channels = 3
height = 1000
width = 1000

def get_datasets(imgs_dir,mask_dir,Nimgs):
    '''
    input:
        imgs_dir: original images
        mask_dir: boundary mask of each image
    output:
        nd-array of imgs
        nd-array of masks(ternary mask)
    '''
    imgs = np.empty((Nimgs,height,width,channels))
    masks = np.empty((Nimgs,height,width,1))

    image_filenames = glob.glob(imgs_dir + '*.jpg')
    for index,filename in enumerate(image_filenames):
        basename = os.path.basename(filename)
        print("original image: " + basename)
        img = Image.open(filename)
        imgs[index] = np.asarray(img)

        inside_mask = mask_dir + basename.split('.')[0] + '_mask_inside.bmp'
        boundary_mask = mask_dir + basename.split('.')[0] + '_mask_bound.bmp'
        mask = generate_ternary_masks(inside_mask,boundary_mask)
        masks[index] = mask

    assert(np.max(masks) == 255 and np.min(masks) == 0)

    #reshaping for my standard tensors
#    imgs = np.transpose(imgs,(0,3,1,2))
    
    
    
    masks = np.reshape(masks,(Nimgs,height,width,1))
    assert(imgs.shape == (Nimgs,height,width,channels))
    assert(masks.shape == (Nimgs,height,width,1))

    
    return imgs,masks

#because images don't have the same size, so we also extract patches from it and save patches into hdf5
def get_normalized_datasets(imgs_dir, mask_dir):
    image_filenames = glob.glob(imgs_dir + '*')
    Npatches = 120000
    patch_w = 51
    patch_h = 51
    

    #save for current number of patches
    iter_tot = 0
    set_num = 0
    for index,filename in enumerate(image_filenames):
        if iter_tot == 0:
            dataset_name = 'set' + str(set_num)
            set_num += 1
            img_patches = np.empty((Npatches, patch_h, patch_w, channels))
            mask_patches = np.empty((Npatches, 3))
            
        #save for patches from single image
        k = 0
        basename = os.path.basename(filename)
        print("original image: " + basename)
        img = Image.open(filename)
        img_w, img_h = img.size
        patch_per_class = 20000
        
        
        inside_mask = mask_dir + basename.split('.')[0] + '_mask_inside.bmp'
        boundary_mask = mask_dir + basename.split('.')[0] + '_mask_bound.bmp'
        mask = generate_ternary_masks(inside_mask,boundary_mask)
        
        img_array = np.asarray(img)
        mask_array = mask
        
        counter = {0:0,1:0,2:0}
        
        while k < 60000 and iter_tot < Npatches:
            
            x_center = random.randint(0+int(patch_w/2),img_w - int(patch_w/2) - 1)
            
            y_center = random.randint(0+int(patch_h/2),img_h - int(patch_h/2) - 1)

            # 0 is background
            # 1 is boundary
            # 2 is inside
            center_label = int(mask_array[y_center,x_center]/127)
            
            if counter[center_label] < patch_per_class:
#                print("image:{}, {} class has: {}".format(i,full_masks[i,0,y_center,x_center],counter[full_masks[i,0,y_center,x_center]]))
                patch_img = img_array[y_center - int(patch_h/2):y_center + int(patch_h/2)+1,x_center - int(patch_w/2):x_center + int(patch_w/2) + 1,:]
                
                img_patches[iter_tot] = patch_img
                if  center_label == 255:
                    mask_patches[iter_tot,0]=0
                    mask_patches[iter_tot,1]=0
                    mask_patches[iter_tot,2]=1
                elif center_label == 127:
                    mask_patches[iter_tot,0]=0
                    mask_patches[iter_tot,1]=1
                    mask_patches[iter_tot,2]=0
                    
                else:
                    mask_patches[iter_tot,0]=0
                    mask_patches[iter_tot,1]=0
                    mask_patches[iter_tot,2]=1
                    
                counter[center_label] += 1
                iter_tot += 1
                k += 1
        if iter_tot == Npatches:
            assert(img_patches.shape == (Npatches,patch_h,patch_w,channels))
            assert(mask_patches.shape == (Npatches,3))
            print("write file")
            write_hdf5(img_patches,'./hdf_dataset/dataset_imgs_train.hdf5',dataset_name)
            write_hdf5(mask_patches, './hdf_dataset/dataset_masks_train.hdf5',dataset_name)
            iter_tot == 0
            counter = {0:0,1:0,2:0}
        print(counter)
#    img_patches = np.transpose(img_patches,(0,3,1,2))

    
if __name__ == '__main__':

    dataset_root = "./hdf_dataset/"
    
    if not os.path.exists(dataset_root):
        os.makedirs(dataset_root)
#===============================Get Original dataset ==============================================
#    train_images = './dataset/train/'
#    mask_path = './dataset/train_mask/'
#    
#    #Get training dataset
#    imgs_train, masks_train = get_datasets(train_images, mask_path,16)
#    write_hdf5(imgs_train,dataset_root + 'dataset_imgs_train.hdf5')
#    write_hdf5(masks_train,dataset_root + 'dataset_masks_train.hdf5')
    
    
#=======================Get the normalized dataset from 9 images==============================
    train_images = './dataset/all_images/'
    mask_path = './dataset/all_masks/'
    
    get_normalized_datasets(train_images,mask_path)

