import pydicom as dicom
import matplotlib.pylab as plt
import glob
import csv

""" things we need for ManiT and dicom processing: 
        - PatientID
        - PatientSex
        - PatientWeight
        - Modality 
        - StudyDate
        - SeriesDescription
"""

def setPatientWeight(ds,weight):
    """
    This function is designed to set 'Patient Weight' in a stack of dicom

    Args:
        ds: dicom object
        weight: (float) patient weight

    Returns:

    """
    ds.PatientWeight = weight

    return

def setPatientSex(ds,sex):
    """
    This function is designed to set 'Patient Sex' in a stack of dicom

    Args:
        ds: dicom object
        sex: (str) patient sex

    Returns:

    """
    ds.PatientSex = sex

    return

#####
#####

cases = sorted(glob.glob('data/*.dcm'))

patients = 0
subfolders = 0
filesNum = 0
for c in cases:
    sub_path = sorted(glob.glob(c+'/*'))
    for s in sub_path:
        image_path = sorted(glob.glob(s+'/*.dcm'))
        for i in image_path:
            ds = dicom.filereader.dcmread(i)
            # ds.PatientSex = 'M'
            ds.add_new([0x0008, 0x103E], 'LO', "Whole Body Scan") # this is found from the standard dicom element structure online.
            # ds.
            # print(ds)
            ds.save_as(i)
            filesNum += 1
            # print(ds)
        subfolders += 1

    # ds = dicom.filereader.dcmread(sorted(glob.glob(sub_path[1]+'/*.dcm'))[0])
    # with open('data_output/study_additional_data.csv', 'a') as f:
    #     if patients == 0:
    #         f.write('Patient ID, Study ID, Study Date, Sex, Age, Weight, Institution Name, Manufacturer Model Name\n')
    #     f.write('%s, %s, %s, %s, %s, %s, %s, %s\n' % (ds.PatientID, ds.StudyID, ds.StudyDate, ds.PatientSex, ds.PatientAge, ds.PatientWeight, ds.InstitutionName, ds.ManufacturerModelName))
    #     #f.write('%s, %s, %s, %s, %s' % (ds.StudyID, ds.StudyDate, ds.PatientSex, ds.InstitutionName, ds.ManufacturerModelName))
    patients += 1
# if you need to edit patient weight:
# setWeightNumber = float(102.15)
# print(ds.PatientWeight)
# ds.PatientWeight = setWeightNumber
print('finished: ', patients)
print('sub folders: ', subfolders)
print('file Number: ', filesNum)

