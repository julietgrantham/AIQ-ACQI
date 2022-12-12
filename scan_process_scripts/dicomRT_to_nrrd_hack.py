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
import pydicom
from dcmrtstruct2nii import dcmrtstruct2nii, list_rt_structs
import dicom2nifti
import nibabel as nib
import nrrd
import glob
import os
import numpy as np
from collections import OrderedDict

def main_dicom_to_nii(root_study_dir, output_root):
    subject_dir = sorted(glob.glob(root_study_dir + '*'))
    for subject in subject_dir:
        print(subject)
        scans = sorted(glob.glob(subject + '/*'))
        for scan in scans:
            image_folder_type = sorted(glob.glob(scan + '/*'))
            # output_folder = scan + '/'
            output_folder = output_root + scan.split('/')[-1] + '/'
            os.mkdir(output_folder)
            
            print(output_folder)
            for folder_type in image_folder_type:
                if 'CT' in folder_type.split('/')[-1]:
                    # converts directory of CT/PET dicom to nii
                    dicom2nifti.convert_directory(folder_type, output_folder)
                    print('written CT: ', output_folder)
                elif 'PT' in folder_type.split('/')[-1]:
                    # converts directory of CT/PET dicom to nii
                    dicom2nifti.convert_directory(folder_type, output_folder)
                    print('written PT: ', output_folder)
                elif 'RTst' in folder_type.split('/')[-1]:
                    rt_file = sorted(glob.glob(folder_type + '/*.dcm'))
                    dicom_file_path = sorted(glob.glob(os.path.split(folder_type)[-2] + '/CT*'))
                    # converts rt struct dicom file to nii but needs dicom folder
                    dcmrtstruct2nii(rt_file[0], dicom_file_path[0], output_folder)
                    print('written RT: ', output_folder)


def main_nii_to_nrrd(root_study_dir, output_root):
    #
    # nii_file = '../data/Jake_PSM/00_testing/nii_output_dir/image.nii.gz'
    subjects_scans = [os.path.basename(f) for f in sorted(glob.glob(root_study_dir + 'MEL*'))]
    # temp_subjects = [os.path.basename(f) for f in sorted(glob.glob('temp_processing/' + 'PS*/PS*'))]

    for sub in subjects_scans:
        nii_files = sorted(glob.glob(root_study_dir+sub+'/*.nii.*'))
        ct_dir = glob.glob(root_study_dir.split('/')[0] + '/' + root_study_dir.split('/')[1] + '/*/' + sub)
        # ct_dir = 'temp_processing/' + sub.split('_')[0] + '/' + sub + '/'
        ct_dicom = [pydicom.dcmread(f) for f in sorted(glob.glob(ct_dir + 'CT*/*.dcm'))]
        output_folder = output_root + sub + '/'
        os.mkdir(output_folder)
        # print('subject: ', sub)
        # print('nii files: ', nii_files)
        # print('ct: ', ct_dir)
        for nii_file in nii_files:
            a = nib.load(nii_file)
            image3d = a.get_fdata()
            header_info = generate_nrrd_header(ct_dicom, image3d)
            output_file_name = output_folder + os.path.basename(nii_file).split('.')[0] + '.nrrd'
            nrrd.write(output_file_name, image3d, header_info)
            print('wrote: ', output_file_name)
    #     a_image_data = a.get_fdata()
    #     f_name = os.path.basename(nii_file).split('.')[0] + '.nrrd'
    #     nrrd.write('ProjectScripts/Australia/processed_nrrd_data/'+f_name, a_image_data, headerInfo)


def generate_nrrd_header(ds,img3d):
    # type, dimensions, space = 'left-posterior-superior', sizes, space direction, encoding, endian, kinds, space origin
    z_max_pos = ds[0].ImagePositionPatient[2]
    for ds_ct in ds:
        if abs(ds_ct.ImagePositionPatient[2]) > z_max_pos:
            z_max_pos = ds_ct.ImagePositionPatient[2]

    image_start = np.asarray((ds[0].ImagePositionPatient[0], ds[0].ImagePositionPatient[1], z_max_pos))
    nrrd_header = OrderedDict()

    nrrd_header['type'] = 'short'  # this gets overridden by the img3d data type
    nrrd_header['dimension'] = 3
    nrrd_header['space'] = 'left-posterior-superior'

    nrrd_header['sizes'] = np.array(img3d.shape)
    nrrd_header['space directions'] = np.array([[ds[0].PixelSpacing[0], 0, 0],
                                                [0, ds[0].PixelSpacing[1], 0],
                                                [0, 0, ds[0].SliceThickness]])
    nrrd_header['encoding'] = 'gzip'
    nrrd_header['endian'] = 'little'
    nrrd_header['kinds'] = ('domain', 'domain', 'domain')
    nrrd_header['space origin'] = np.array(image_start)

    return nrrd_header


if __name__ == "__main__":
    print('running...')
    # root_study_dir = 'temp_processing/'
    root_study_dir = 'D:/Melanoma01/FinalTrainingCohort_AIQ_Mel01_Corrected/Final_Mel01'
    # output_root = 'processed_nii_data/'
    output_root = 'D:/Melanoma01/FinalTrainingCohort_AIQ_Mel01_Corrected/Final_Mel01_nrrd'

    main_dicom_to_nii(root_study_dir, output_root)
    # main_nii_to_nrrd(root_study_dir, output_root)
    
