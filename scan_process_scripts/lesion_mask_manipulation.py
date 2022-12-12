# -*- encoding utf-8 -*-
'''
@File       : .py
@Contact    : username.you@email.address.com
@License    : (C)Copyright AIQ Solutions 2022

@ModifyTime     @Author     @Version        @Description
-----------     -------     --------        ------------
  username    1.0             None

Module Documentation: 

'''

import nrrd
import os
import numpy as np
import glob
from collections import OrderedDict

def myLabelStack(label_list):
    """given a list of str types, read in nrrd files and convert into one image array."""
    img3 = 0
    header = OrderedDict()
    for lab in label_list:
        mask = nrrd.read(lab)
        img3 = img3 + mask[0]

    header = mask[1]
    nrrd_img3 = (img3, header)
    return nrrd_img3

def myNormalisedLabelStack(label_list):
    """ given a list of str types, read in nrrd files, normalise values, and convert into one image array.
    returns: (tuple) image stack containing ndarry data and header information. """
    img3 = 0
    header = OrderedDict()
    for lab in label_list:
        mask = nrrd.read(lab)
        img3 = img3 + mask[0]

    header = mask[1] # assume all file headers are the same and can just take the last one.
    img3_stack = (myNormaliseLabelImg3d(img3), header)
    return img3_stack

def myNormaliseLabelImg3d(img3):
    """ given an 3D ndarry, normalise the data values and return. """
    img3_normalised = (img3 - np.min(img3))/(np.max(img3) - np.min(img3))
    return img3_normalised

if __name__ == "__main__":
    # for all patients:
    # convert individual lesions into lesion stacks
    # normalise mask into binary mask
    # convert labels of lesions into specific numbers
    root_dir = '../../../local_dev_testing/processed_nrrd_data/'
    subjects = sorted(glob.glob(root_dir+'PS069*')) #'PS001LB'
    subject_id = [os.path.basename(f) for f in subjects]
    
    for s in subjects:
        print('processing: ', s)
        output_dir = s + '/'
        list_of_all_mask = sorted(glob.glob(s+'/*mask*.nrrd'))
        lesion_mask = []
        for mask in list_of_all_mask:
            if 'Ref' not in mask and 'Burden' not in mask:
                lesion_mask.append(mask)
                print(mask)
        lesion_mask_count = len(lesion_mask)
        print('mask total no.: ', lesion_mask_count)
        
        if lesion_mask_count != 0:
            img3d = myNormalisedLabelStack(lesion_mask)
            filename = output_dir + os.path.basename(s) + '_lesion_mask.nrrd'
            nrrd.write(filename, img3d[0], img3d[1])  # str, data, header
            print('written combined lesion mask: ', s)
    
    
    # scans = [sorted(glob.glob(s + '/PS*')) for s in subjects]
    # for scan in subjects:
    #     for s in scan:
    #         output_dir = s + '/' #root_dir + subject_id + '/' + os.path.basename(s) + '/'
    #         list_of_all_mask = sorted(glob.glob(s+'/*mask*.nrrd'))
    #         lesion_mask = []
    #         for mask in list_of_all_mask:
    #             if 'Ref' not in mask:
    #                 lesion_mask.append(mask)
    #         lesion_mask_count = len(lesion_mask)
    #         print('mask total no.: ', lesion_mask_count)
    #         img3d = myNormalisedLabelStack(lesion_mask)
    #         filename = output_dir + os.path.basename(s) + '_lesion_mask.nrrd'
    #         nrrd.write(filename, img3d[0], img3d[1])  # str, data, header

    # mask_region_label_dict = {'44': 'lumbar spine',
    #                           '19': 'the head'}
    #
    # region_mapping_dict = {'head': 1,
    #                        'neck': 2,
    #                        'spine': 3,
    #                        'left femur': 4,
    #                        'right femur': 5}



