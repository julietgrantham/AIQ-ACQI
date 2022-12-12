# -*- encoding utf-8 -*-
'''
@File       : plot_lesion_mips.py
@Contact    : shasha.yeung@aiq-solutions.com
@License    : (C)Copyright AIQ Solutions 2022

@ModifyTime     @Author     @Version        @Description
-----------     -------     --------        ------------
  username    1.0             None

Module Documentation: This script was created to generate lesion mips for the Australian Prostate dataset, using the Sci
code 'plotLesionsFucntion.py' in the utils directory.

'''
import os
import numpy as np
import SimpleITK as sitk
import glob
import nrrd
from collections import OrderedDict

# Lib files
from plotLesionsFunction import plotAndSaveLesions
import medical_image_process as img_loader

def myNormalisedLabelStack(label_list):
    """ given a list of str types, read in nrrd files and convert into one image array."""
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

# load images
main_dir = '/home/shasha/data/*PSMA*testretest*/PatientData_Processed/'
output_dir = 'output_dir/'
patient_sub_string = 'RP_13*'
date_sub = '*scan01*'
ct_dir = [main_dir + f'{patient_sub_string}/{date_sub}/*ct*']
pet_dir = [main_dir + f'{patient_sub_string}/{date_sub}/*pet*']
gtv_dir = [main_dir + f'{patient_sub_string}/{date_sub}/*lesion*']
separate_lesion_MIPs = False


dirs = [ct_dir, pet_dir]
ImList = []
for modal in dirs:
    modal_ims = []
    for directory in modal:
        dir_ims = glob.glob(directory + "*.nrrd")
        pt_labels = [xx.replace('_', '-') for xx in dir_ims]
        inds = np.argsort(pt_labels).astype(int)
        dir_ims = [dir_ims[ii] for ii in inds]
        modal_ims.extend(dir_ims)
    modal_ims.sort()
    ImList.append(modal_ims)

labellist = []
for directory in gtv_dir:
    dir_labs = glob.glob(directory + "*.nrrd")
    pt_labels = [xx.replace('_', '-') for xx in dir_labs]
    inds = np.argsort(pt_labels).astype(int)
    dir_labs = [dir_labs[ii] for ii in inds]
    labellist.extend(dir_labs)
labellist.sort()

# iterate through all CTS
for idx, ct_name in enumerate(ImList[0]):
    folders, fname = os.path.split(ct_name)
    # ID = ID[0:fname.index('_ctData')]
    ID = os.path.split(folders)[-1]

    pet = [xx for xx in ImList[1] if ID in xx]
    label = [xx for xx in labellist if ID in xx]
    output_ID = ID
    if len(label) > 1:
        if separate_lesion_MIPs:
            # if you want to output individual lesions per MIP
            if len(label) > 0:
                for l in label:
                    output_ID = ID + '_' + os.path.split(l)[-1].split('_')[-1].split('.')[0]
                    if len(pet) > 0:
                        CT, PET, GT, img_info = img_loader.load_PETCT_images([ct_name, pet[0], l],
                                                                             resample_voxel_size=[2, 2, 2],
                                                                             fillEmpty=False)
                        toplot = np.stack((CT, PET))
                        imtype = 'PETCT'
                    else:
                        CT, GT, img_info = img_loader.load_CT_images([ct_name, l],
                                                                     resample_voxel_size=[1, 1, 1],
                                                                     fillEmpty=False)
                        toplot = CT
                        imtype = 'CT'

                    plotAndSaveLesions(main_dir + output_dir,
                                       output_ID,
                                       toplot, GT, np.zeros(GT.shape),
                                       imtype=imtype,
                                       should_plot_lesion_numbers=True,
                                       should_plot_response=False,
                                       concat_axis=1)
        elif not separate_lesion_MIPs:
            # stack labels together
            print('try stacking')
            new_label_stack = myNormalisedLabelStack(label)
            filename = main_dir + output_dir + output_ID + '_stacked_lesions.nrrd'
            nrrd.write(filename, new_label_stack[0], new_label_stack[1])  # str, data, header

            if len(pet) > 0:
                CT, PET, GT, img_info = img_loader.load_PETCT_images([ct_name, pet[0], filename],
                                                                     resample_voxel_size=[2, 2, 2],
                                                                     fillEmpty=False)
                toplot = np.stack((CT, PET))
                imtype = 'PETCT'
            else:
                CT, GT, img_info = img_loader.load_CT_images([ct_name, filename],
                                                             resample_voxel_size=[1, 1, 1],
                                                             fillEmpty=False)
                toplot = CT
                imtype = 'CT'
            print('plotting lesion response.')
            plotAndSaveLesions(main_dir + output_dir,
                               output_ID,
                               toplot, GT, np.zeros(GT.shape),
                               imtype=imtype,
                               should_plot_lesion_numbers=True,
                               should_plot_response=True,
                               concat_axis=1)

    elif len(label) == 1:
        # there is only 1 label
        if len(pet) > 0:
            CT, PET, GT, img_info = img_loader.load_PETCT_images([ct_name, pet[0], label[0]],
                                                                 resample_voxel_size=[2, 2, 2],
                                                                 fillEmpty=False)
            toplot = np.stack((CT, PET))
            imtype = 'PETCT'
        else:
            CT, GT, img_info = img_loader.load_CT_images([ct_name, label[0]],
                                                         resample_voxel_size=[1, 1, 1],
                                                         fillEmpty=False)
            toplot = CT
            imtype = 'CT'

        plotAndSaveLesions(main_dir + output_dir,
                           output_ID,
                           toplot, GT, np.zeros(GT.shape),
                           imtype=imtype,
                           should_plot_lesion_numbers=True,
                           should_plot_response=False,
                           concat_axis=1)
    else:
        # there is no lables
        print('can not find labels')

print('Done!')
