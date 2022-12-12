import nibabel as nib
import SimpleITK as sitk
import numpy as np
import torch
import glob
import os
import pandas as pd
from scipy import ndimage

"""
concentrate all pre-processing here here
"""


def load_CT_images(paths, resample_voxel_size=None, 
                   normalization = False, fillEmpty=True,
                   return_torch = False):
    """
    LOAD_CT_IMAGES: deprecated? Wraps load_medical_image

    Parameters
    ----------
    paths : TYPE
        DESCRIPTION.
    resample_voxel_size : TYPE, optional
        DESCRIPTION. The default is None.
    normalization : TYPE, optional
        DESCRIPTION. The default is False.
    fillEmpty : TYPE, optional
        DESCRIPTION. The default is True.
    return_torch : TYPE, optional
        DESCRIPTION. The default is False.

    Returns
    -------
    TYPE
        DESCRIPTION.
    TYPE
        DESCRIPTION.
    img_info : TYPE
        DESCRIPTION.

    """

    ct_np, ct_original_img = load_medical_image(paths[0], type = 'CT',
                                                resample_voxel_size = resample_voxel_size,
                                                fillEmpty=fillEmpty)
    
    if len(paths)==2:
        label_np, label_original_img = load_medical_image(paths[1], type = 'label',
                                                reference_image = paths[0],
                                                resample_voxel_size = resample_voxel_size)
    else: 
        label_np = np.zeros(1)
        label_original_img = None
        
    ct_np[ct_np<-1024]=-1024

    if normalization:
        # 3. intensity normalization    
        ctmean = np.mean(ct_np[ct_np>-500])
        ctstd = np.std(ct_np[ct_np>-500])
        ct_np = ct_np - ctmean
        ct_np = np.divide(ct_np, ctstd)
        
    img_info = []
    img_info.append(ct_original_img)
    img_info.append(label_original_img)

    if return_torch:   
        return torch.from_numpy(ct_np.copy()), torch.from_numpy(label_np.copy()), img_info
    else:
        return ct_np, label_np, img_info
    
def load_PETCT_images(paths, resample_voxel_size = None, 
                      normalization = False, fillEmpty=True, 
                      reference_image_index = 0, #default CT is the reference image, 
                      return_torch = False):
    """
    LOAD_PETCT_IMAGES: deprecated? delete? Wraps load_medical_image

    Parameters
    ----------
    paths : TYPE
        DESCRIPTION.
    resample_voxel_size : TYPE, optional
        DESCRIPTION. The default is None.
    normalization : TYPE, optional
        DESCRIPTION. The default is False.
    fillEmpty : TYPE, optional
        DESCRIPTION. The default is True.
    reference_image_index : int, optional
        Index of reference image. 0=CT, 1=PET, 2=labels.
        All images will be loaded on this grid. The default is 0.
    #default CT is the reference image : TYPE
        DESCRIPTION.
    return_torch : TYPE, optional
        DESCRIPTION. The default is False.

    Returns
    -------
    TYPE
        DESCRIPTION.
    TYPE
        DESCRIPTION.
    TYPE
        DESCRIPTION.
    img_info : TYPE
        DESCRIPTION.

    """
    
                          
    ct_np, ct_original_img = load_medical_image(paths[0], type = 'CT',
                                                reference_image = paths[reference_image_index],
                                                resample_voxel_size = resample_voxel_size, 
                                                fillEmpty=fillEmpty)
    pet_np, pet_original_img = load_medical_image(paths[1], type = 'PET',
                                                  reference_image = paths[reference_image_index],
                                                  resample_voxel_size = resample_voxel_size)
    if len(paths)==3:
        label_np, label_original_img = load_medical_image(paths[2], type = 'label',
                                                reference_image = paths[reference_image_index],
                                                resample_voxel_size = resample_voxel_size)
    else:
        label_np = np.zeros(1)
        label_original_img = None

    ct_np[ct_np<-1024]=-1024
    
    if normalization:
        # 3. intensity normalization    
        ctmean = np.mean(ct_np[ct_np>-500])
        ctstd = np.std(ct_np[ct_np>-500])
        ct_np = ct_np - ctmean
        ct_np = np.divide(ct_np, ctstd)
        
        petmean = np.mean(pet_np[pet_np>0.01])
        petstd = np.std(pet_np[pet_np>0.01])
        pet_np = pet_np - petmean
        pet_np = np.divide(pet_np, petstd)
                
    img_info = []
    img_info.append(ct_original_img)
    img_info.append(pet_original_img)
    img_info.append(label_original_img)

    if return_torch:   
        return torch.from_numpy(ct_np.copy()), torch.from_numpy(pet_np.copy()), torch.from_numpy(label_np.copy()), img_info
    else:
        return ct_np, pet_np, label_np, img_info
   
def load_medical_image(path, type=None, reference_image = None, 
                       resample_voxel_size=None, fillEmpty=False, 
                       return_original_sitk = True):
    """
    LOAD_MEDICAL_IMAGE: load a .nrrd or .nii image. Wraps load_image_with_sitk.

    Parameters
    ----------
    path : str
        Path to image file.
    type : TYPE, optional
        DESCRIPTION. The default is None.
    reference_image : str, optional
        Path to a reference image. If provided, the image at path will be resampled
        so that shape(path)=shape(reference_image). The default is None.
    resample_voxel_size : TYPE, optional
        DESCRIPTION. The default is None.
    fillEmpty : boolean, optional
        DESCRIPTION. The default is False.
    return_original_sitk : boolean, optional
        DESCRIPTION. The default is True.

    Returns
    -------
    img_np : numpy array
        DESCRIPTION.
    img_sitk : sitk image object
        DESCRIPTION.

    """
    
    if type == 'label':
        resample_type = 'nearest'
    else:
        resample_type = 'linear'
    if type == 'CT':
        default_pixel = -1024
    else:
        default_pixel = 0
    
    if 'VISCERAL' in path:#or 'BTCV' in path or 'pancreasCT' in path:
        img_np, original_img_info = load_image_with_nibabel(path, resample_voxel_size, resample_type)
    else:
        original_img_info = load_image_with_sitk(path, reference_image = None, 
                                                 default_pixel = None,
                                                 resample_type = None)  # load image without any processing
        img_sitk = load_image_with_sitk(path, reference_image, default_pixel, resample_type) 
        if type=='CT' and fillEmpty:
            ct_np = fill_empty_slices(sitk_to_np(img_sitk))
            img_sitk_new = np_to_sitk(ct_np)
            img_sitk_new.CopyInformation(img_sitk)
            img_sitk=img_sitk_new
        if resample_voxel_size is not None:
            img_sitk = resample_sitk_image(img_sitk, resample_voxel_size, resample_type = resample_type, defaultvoxel = default_pixel)
        img_np = sitk_to_np(img_sitk)
        
    if type=='label':
        img_np = img_np.astype(np.int16)
    else:
        img_np = img_np.astype(np.float64)
    if return_original_sitk:
        return img_np, original_img_info
    else:
        return img_np, img_sitk

def sitk_to_np(image):
    """
    SITK_TO_NP: 

    Parameters
    ----------
    image : TYPE
        DESCRIPTION.

    Returns
    -------
    image_np : TYPE
        DESCRIPTION.

    """
    
    image_np = np.rot90( np.fliplr( np.moveaxis( sitk.GetArrayFromImage(image), 0, -1) ), 3)
    return image_np

def sitk_to_np_product(image: sitk.Image) -> np.ndarray:
    """
    SITK_TO_NP_PRODUCT: 

    Parameters
    ----------
    image : sitk.Image
        DESCRIPTION.

    Returns
    -------
    data : TYPE
        DESCRIPTION.

    """
    
    data = sitk.GetArrayFromImage(image).swapaxes(0, 2)
    return data

def np_to_sitk_coords(image):
    """
    NP_TO_SITK_COORDS: 

    Parameters
    ----------
    image : TYPE
        DESCRIPTION.

    Returns
    -------
    image : TYPE
        DESCRIPTION.

    """
    
    image = np.rot90(image, 1)
    image = np.fliplr(image)
    image = np.moveaxis(image, -1, 0)
    return image
        

def np_to_sitk(image):
    """
    NP_TO_SITK: 

    Parameters
    ----------
    image : TYPE
        DESCRIPTION.

    Returns
    -------
    image : TYPE
        DESCRIPTION.

    """
    
    image = np.rot90(image, 1)
    image = np.fliplr(image)
    image = np.moveaxis(image, -1, 0)
    image = sitk.GetImageFromArray(image)
    return image
        
 
def resample_sitk_image(image, new_voxel_size, resample_type, defaultvoxel):
    """
    RESAMPLE_SITK_IMAGE: 

    Parameters
    ----------
    image : TYPE
        DESCRIPTION.
    new_voxel_size : TYPE
        DESCRIPTION.
    resample_type : TYPE
        DESCRIPTION.
    defaultvoxel : TYPE
        DESCRIPTION.

    Returns
    -------
    new_image : TYPE
        DESCRIPTION.

    """
    
    resample_filter = sitk.ResampleImageFilter()
    resample_filter.SetReferenceImage(image)
    original_spacing = image.GetSpacing()
    original_size = image.GetSize()
    out_spacing = new_voxel_size
    out_size = [
        int(np.round(original_size[0] * (original_spacing[0] / out_spacing[0]))),
        int(np.round(original_size[1] * (original_spacing[1] / out_spacing[1]))),
        int(np.round(original_size[2] * (original_spacing[2] / out_spacing[2])))]
    resample_filter.SetOutputSpacing(new_voxel_size)
    resample_filter.SetSize(np.array(out_size).tolist())
    resample_filter.SetDefaultPixelValue(defaultvoxel)
    if resample_type == 'nearest':
        resample_filter.SetInterpolator(sitk.sitkNearestNeighbor)
    new_image = resample_filter.Execute(image)
    return new_image

def load_image_with_sitk(path, reference_image, default_pixel, resample_type):
    """
    LOAD_IMAGE_WITH_SITK:

    Parameters
    ----------
    path : TYPE
        DESCRIPTION.
    reference_image : TYPE
        DESCRIPTION.
    default_pixel : TYPE
        DESCRIPTION.
    resample_type : TYPE
        DESCRIPTION.

    Returns
    -------
    img_info_new : TYPE
        DESCRIPTION.

    """
    
    # load the image 
    reader = sitk.ImageFileReader()
    reader.SetFileName(path)
    img_info = reader.Execute()
        
    # if we need to resample the image to a different reference image (e.g., CT to PET)
    if reference_image is not None and path!=reference_image:
        reader.SetFileName(reference_image)
        ref_image = reader.Execute()
        
        resample_filter = sitk.ResampleImageFilter()
        resample_filter.SetReferenceImage(ref_image)  
        
        #resample with nearest neighbor to preserve image values
        if resample_type == 'nearest':
            resample_filter.SetInterpolator(sitk.sitkNearestNeighbor)
        if default_pixel!=0:
            resample_filter.SetDefaultPixelValue(default_pixel)
        img_info_new = resample_filter.Execute(img_info)
        
    else:
        img_info_new = img_info
        
    return img_info_new

def resample_to_reference_im(img, ref_image, default_pixel, resample_type):
    """
    RESAMPLE_TO_REFERENCE_IM:

    Parameters
    ----------
    img : TYPE
        DESCRIPTION.
    ref_image : TYPE
        DESCRIPTION.
    default_pixel : TYPE
        DESCRIPTION.
    resample_type : TYPE
        DESCRIPTION.

    Returns
    -------
    img_info_new : TYPE
        DESCRIPTION.

    """
    
        
    resample_filter = sitk.ResampleImageFilter()
    resample_filter.SetReferenceImage(ref_image)  
        
    #resample with nearest neighbor to preserve image values
    if resample_type == 'nearest':
        resample_filter.SetInterpolator(sitk.sitkNearestNeighbor)
    if default_pixel!=0:
        resample_filter.SetDefaultPixelValue(default_pixel)
    img_info_new = resample_filter.Execute(img)
        
    return img_info_new


def load_image_with_nibabel(path, type, resample = None, fillEmpty = False):
    """
    LOAD_IMAGE_WITH_NIBABEL: deprecated? Delete?

    Parameters
    ----------
    path : TYPE
        DESCRIPTION.
    type : TYPE
        DESCRIPTION.
    resample : TYPE, optional
        DESCRIPTION. The default is None.
    fillEmpty : TYPE, optional
        DESCRIPTION. The default is False.

    Returns
    -------
    img_np : TYPE
        DESCRIPTION.
    original_img_info : TYPE
        DESCRIPTION.

    """
    
    img_nii = nib.load(path)
    voxel_size = img_nii.header.get_zooms()
    img_nii = nib.as_closest_canonical(img_nii)
           
    original_img_info = img_nii.get_affine()
    img_np = np.squeeze(img_nii.get_fdata(dtype=np.float32))
 
    if resample is not None: 
        new_shape = np.round(((np.array(voxel_size) / np.array(resample)).astype(float) * np.asarray(img_np.shape))).astype(int)
    
        if type!='label':
            img_np = rescale_data_volume(img_np, new_shape, interp_order=3)
        else:
            img_np = rescale_data_volume(img_np, new_shape, interp_order=0)
    return img_np, original_img_info

def rescale_data_volume(img_numpy, out_dim, interp_order=0):
    """
    RESCALE_DATA_VOLUME:Resize the 3d numpy array to the dim size

    Parameters
    ----------
    img_numpy : numpy array of shape
        DESCRIPTION.
    out_dim : tuple of shape (3,)
        out_dim is the new 3d tuple.
    interp_order : TYPE, optional
        DESCRIPTION. The default is 0.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """

    if img_numpy.ndim == 2:
        depth, height = img_numpy.shape
        scale = [out_dim[0] * 1.0 / depth, out_dim[1] * 1.0 / height]
    else:
        depth, height, width = img_numpy.shape
        scale = [out_dim[0] * 1.0 / depth, out_dim[1] * 1.0 / height, out_dim[2] * 1.0 / width]
    return ndimage.interpolation.zoom(img_numpy, scale, order = interp_order)



def normalize_intensity(img_tensor, normalization="max_min", norm_values=(0, 1, 1, 0)):
    """
    NORMALIZE_INTENSITY: Accepts an image tensor and normalizes it

    Parameters
    ----------
    img_tensor : TYPE
        DESCRIPTION.
    normalization : str, optional
        choices = "max", "mean". The default is "max_min".
    norm_values : TYPE, optional
        DESCRIPTION. The default is (0, 1, 1, 0).

    Returns
    -------
    TYPE
        DESCRIPTION.
        
    """
    if normalization == "mean":
        mask = img_tensor.ne(0.0)
        desired = img_tensor[mask]
        mean_val, std_val = desired.mean(), desired.std()
        img_tensor = (img_tensor - mean_val) / std_val
    elif normalization == "max":
        max_val, _ = torch.max(img_tensor)
        img_tensor = img_tensor / max_val
    elif normalization == 'brats':
        # print(norm_values)
        normalized_tensor = (img_tensor.clone() - norm_values[0]) / norm_values[1]
        final_tensor = torch.where(img_tensor == 0., img_tensor, normalized_tensor)
        final_tensor = 100.0 * ((final_tensor.clone() - norm_values[3]) / (norm_values[2] - norm_values[3])) + 10.0
        x = torch.where(img_tensor == 0., img_tensor, final_tensor)
        return x

    elif normalization == 'full_volume_mean':
        img_tensor = (img_tensor.clone() - norm_values[0]) / norm_values[1]

    elif normalization == 'max_min':
        img_tensor = (img_tensor - norm_values[3]) / ((norm_values[2] - norm_values[3]))

    elif normalization == None:
        img_tensor = img_tensor
    return img_tensor

def fill_empty_slices(img_numpy):
    """
    FILL_EMPTY_SLICES: 

    Parameters
    ----------
    img_numpy : TYPE
        DESCRIPTION.

    Returns
    -------
    img_numpy : TYPE
        DESCRIPTION.

    """
    
    img_numpy[img_numpy<-1000] = -1000
    max_per_slice = np.max(np.max(img_numpy, axis=0), axis=0)
    #empty_slices = [xx for xx in range(1, len(max_per_slice)-1) if abs(max_per_slice[xx+1]-max_per_slice[xx])>500]
    empty_slices = [xx for xx in range(1, len(max_per_slice)-1) if max_per_slice[xx] <= -1000 or max_per_slice[xx]>=5000] #and max_per_slice[xx+1] != -1000 and max_per_slice[xx-1] != -1000]
    
    double_empty_slices = [xx for xx in range(2, len(max_per_slice)-2) if max_per_slice[xx] == -1000 and xx not in empty_slices]
    for sl in empty_slices: 
        if sl>0 and  sl<len(max_per_slice):
            img_numpy[:,:,sl] = (img_numpy[:,:,sl-1] + img_numpy[:,:,sl+1]) / 2
        
    for xx in range(len(double_empty_slices)//2) :
        if ((double_empty_slices[xx]-1)>0) and ((double_empty_slices[xx]+1)<len(max_per_slice)):
            sl = double_empty_slices[xx*2]
            img_numpy[:,:,sl] = (0.75*img_numpy[:,:,sl-1] + 0.25*img_numpy[:,:,sl+2]) 
            img_numpy[:,:,sl+1] = (0.25*img_numpy[:,:,sl-1] + 0.75*img_numpy[:,:,sl+2]) 
       

    return img_numpy

def crop_img(img_tensor, crop_size, crop):
    """
    CROP_IMG: 

    Parameters
    ----------
    img_tensor : TYPE
        DESCRIPTION.
    crop_size : TYPE
        DESCRIPTION.
    crop : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    
    if crop_size[0] == 0:
        return img_tensor
    slices_crop, w_crop, h_crop = crop
    dim1, dim2, dim3 = crop_size
    inp_img_dim = img_tensor.dim()
    assert inp_img_dim >= 3
    if img_tensor.dim() == 3:
        full_dim1, full_dim2, full_dim3 = img_tensor.shape
    elif img_tensor.dim() == 4:
        _, full_dim1, full_dim2, full_dim3 = img_tensor.shape
        img_tensor = img_tensor[0, ...]
    if full_dim1 == dim1 and full_dim2 == dim2 and full_dim3 == dim3:
        img_tensor = img_tensor
    elif full_dim1 == dim1 and full_dim2 == dim2:
        img_tensor = img_tensor[:, :,
                     h_crop:h_crop + dim3]
    elif full_dim1 == dim1 and full_dim3 == dim3:
        img_tensor = img_tensor[:, w_crop:w_crop+dim2, :]
    elif full_dim2 == dim2 and full_dim3 == dim3:
        img_tensor = img_tensor[slices_crop:slices_crop + dim1, :, :]
    elif full_dim1 == dim1:
        img_tensor = img_tensor[:, w_crop:w_crop + dim2,
                     h_crop:h_crop + dim3]
    elif full_dim2 == dim2:
        img_tensor = img_tensor[slices_crop:slices_crop + dim1, :,
                     h_crop:h_crop + dim3]
    elif full_dim3 == dim3:
        img_tensor = img_tensor[slices_crop:slices_crop + dim1, w_crop:w_crop + dim2, :]
    else:
        img_tensor = img_tensor[slices_crop:slices_crop + dim1, w_crop:w_crop + dim2,
                     h_crop:h_crop + dim3]

    if inp_img_dim == 4:
        return img_tensor.unsqueeze(0)

    return img_tensor

def save_3d_vol(img_info, save_path):
    """
    SAVE_3D_VOL:

    Parameters
    ----------
    img_info : TYPE
        DESCRIPTION.
    save_path : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    
    directory,_ = os.path.split(save_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    ifw = sitk.ImageFileWriter()
    ifw.SetFileName(save_path)
    ifw.SetUseCompression(True)
    ifw.Execute(img_info)
   

def removetable(ctim):
    """
    REMOVETABLE:

    Parameters
    ----------
    ctim : numpy array
        CT image volume.

    Returns
    -------
    None.

    """
    
    notair = ctim>-600
    
    axial_integral_lines = np.std(ctim, 2)
    