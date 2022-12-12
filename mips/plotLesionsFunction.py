# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 12:06:36 2020

@author: amy.weisman
"""

# -*- coding: utf-8 -*-
"""

Created on Sun Oct 25 20:08:10 2020

@author: amy.weisman
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import fastremap
# Lib files
from skimage.transform import resize
import nrrd

def Gradient(c1,c2,steps):
    """
    GRADIENT: 

    Parameters
    ----------
    c1 : TYPE
        DESCRIPTION.
    c2 : TYPE
        DESCRIPTION.
    steps : TYPE
        DESCRIPTION.

    Returns
    -------
    gradient : TYPE
        DESCRIPTION.

    """
    
    gradient = []
    for j in range(steps):
        t = j/steps
        toappend = (c1[0]+(c2[0]-c1[0])*t,c1[1]+(c2[1]-c1[1])*t,c1[2]+(c2[2]-c1[2])*t)
        gradient.append(toappend)
    return gradient
            
def get_pet_heat_colormap():
    """
    GET_PET_HEAT_COLORMAP: using a defined gradient create a matplotlib colourmap object table of defined colours.

    Returns
    -------
    mymap : (object) - matplotlib colourmap object look up table using linear segment of 0-1 for colour values.

    """
    
    colors1 = Gradient((1, 1, 1), (0, 0, 0), 15)
    colors2 = Gradient((0, 0, 0), (168/255, 21/255, 0), 20)
    colors3 = Gradient((168/255, 21/255, 0), (1, 1, 0), 20)
    colors4 = Gradient((1, 1, 0), (1, 1, 1), 40)
    
    colors = np.vstack((colors1, colors2, colors3, colors4))
    mymap = mcolors.LinearSegmentedColormap.from_list('petheat', colors)
    return mymap


def center_of_mass(region: np.ndarray):
    """
    CENTER_OF_MASS: find the "center" of a region to plot the region's label

    Parameters
    ----------
    region : np.ndarray
        ROI mask (one ROI?).

    Returns
    -------
    np.ndarray shape (2,)
        x, y coordinates of the center of the region in the image
    """
    
    x = region[:, 0]
    y = region[:, 1]
    g = x[:-1] * y[1:] - x[1:] * y[:-1]
    a = 0.5 * g.sum()
    cx = ((x[:-1] + x[1:]) * g).sum()
    cy = ((y[:-1] + y[1:]) * g).sum()
    return (1.0 / (6 * a)) * np.array([cx, cy])

def make_mip(image, concat_axis):
    """
    MAKE_MIP: 

    Parameters
    ----------
    image : TYPE
        DESCRIPTION.
    concat_axis : int
        DESCRIPTION.

    Returns
    -------
    mips : TYPE
        DESCRIPTION.

    """
    
    mip_sag = np.fliplr(np.rot90(np.max(image, axis=0)))
    mip_cor = np.fliplr(np.rot90(np.max(image, axis=1)))
    mips = np.concatenate((mip_cor, mip_sag), axis=concat_axis)
    
    #mips = resize(mips, (2*image.shape[1], mips.shape[1]), preserve_range = True)
    return mips

def plotAndSaveLesions(savedir, subID, image, label, GT, imtype='CT', 
                       should_plot_lesion_numbers=False, should_plot_response = False, 
                       concat_axis = 1, colormap = 'Greys_r'):
    """
    PLOTANDSAVELESIONS:
    Outputs: saved '.png' file of lesion contours.

    Parameters
    ----------
    savedir : (str) path of directory you are wanting to save to.
    subID : (str) subject ID naming convention.
    image : (array) numpy array of scanned image geometry expected.
    label : (array) contour lesion mask label.
    GT : (array) ground true mask label of lesion.
    imtype : (str) specifying image type, options currently accepted for imtype can be 'PET', 'CT', or 'PETCT'.
        * If PET/CT: input for CT should be a 4D array with PET in [0, :, :, :] and CT in [1, :, :, :]
        * The default is 'CT'.
    should_plot_lesion_numbers : (boolean), optional and defaults to False.
    should_plot_response : (boolean), optional and defaults to False.
    concat_axis : (int), optional. Concatenate axis, default set as 1.
    colormap : (str), optional. Can be 'petheat'. The default is 'Greys_r'.

    Returns
    -------
    None.

    """
    # pad the images with one row of zeroes all around to account for lesions that run off the image
    image = np.pad(image, 1, mode='minimum')
    label = np.pad(label, 1, mode='minimum')
    GT = np.pad(GT, 1, mode='minimum')

    print('Processing: ', subID)

    if ('CT' in imtype and not 'PET' in imtype) or ('PET' in imtype and not 'CT' in imtype):
        CTmips = make_mip(image, concat_axis)
    elif 'PETCT' in imtype:
        CTmips = make_mip(image[1, :, :, :], concat_axis)
        PETmips = make_mip(image[0, :, :, :], concat_axis)

    saveFileName = savedir + '/images_results/' + subID + '.png'
    if not os.path.isdir(savedir + '/images_results/'):
        os.makedirs(savedir + '/images_results/')
    
    if 'norm' in imtype:
        if 'PETCT' in imtype:
            minplotct = -1
            maxplotct = 2
            minplotpet = -1
            maxplotpet = 2
        else:
            minplot = -1
            maxplot= 4
    else:
        if imtype == 'CT':
            CTmips = np.divide(CTmips, 1000)*200
            maxplot = 215
            minplot = -135
        elif imtype == 'PET':
            maxplot = 8
            minplot = 0
        else: 
            CTmips = np.divide(CTmips, 1000)*200
            minplotct = -135
            maxplotct = 215
            minplotpet = 0
            maxplotpet = 10
            
    if colormap == 'petheat':
        colormap = get_pet_heat_colormap()  # returns matplotlib colourmap table
        
    if ('CT' in imtype and not 'PET' in imtype) or ('PET' in imtype and not 'CT' in imtype):
        plt.imshow(CTmips,  cmap=colormap, vmin=minplot, vmax=maxplot)
    else:
        plt.imshow(CTmips, cmap='Greys_r', vmin=minplotct, vmax=maxplotct)
        plt.imshow(PETmips, cmap='hot', alpha=0.5, vmin=minplotpet, vmax=maxplotpet)

    if not (should_plot_lesion_numbers or should_plot_response) and np.max(label) > 0:
        labelmips = make_mip(label, concat_axis).astype(np.int16)
        plt.contour(labelmips, colors='m', linewidths=0.3)
    
        if np.any(GT>0):
            GTmips = make_mip(GT, concat_axis).astype(np.int16)
            
            tpl = np.sum(np.logical_and(GT, label))
            fpl = np.sum(np.logical_and(GT==0, label==1))
            fnl = np.sum(np.logical_and(GT==1, label==0))
            dice = (2.0*tpl/(2.0*tpl + fpl + fnl))
            ppv = (tpl / (tpl+fpl))
            sens = (tpl/np.sum(GT))
            
            plt.contour(GTmips, colors='lime', linewidths=0.3) 
            proxy = plt.plot(0,0, 'm', 0, 0, 'lime')
            plt.legend(proxy, ('U-net', 'GT') , fontsize=4)
            plt.text(0.91, 0.4, r'$DSC = $' + str(round(dice, 3)) + '\n'
                                r'$Sens = $' + str(round(sens, 3)) + '\n'
                                r'$PPV = $' + str(round(ppv, 3)) + '\n',
                     transform = plt.gcf().transFigure)
    
    elif (should_plot_lesion_numbers or should_plot_response) and np.max(label)>0:
        if should_plot_response: 
            colors = ['darkgreen', 'lime', 'blue', 'red', 'darkred', 'yellow', 'orange']
            labels = ['disappear', 'decrease', 'stable', 'increase', 'new', 'not in scan1 FOV', 'not in scan2 FOV']
            proxy = plt.plot(0,0, colors[0], 0,0, colors[1], 0,0, colors[2], 0,0,colors[3], 
                             0,0,colors[4], 0,0,colors[5], 0,0, colors[6])
            plt.legend(proxy, labels , fontsize=4)
        else:
            colors = ['red', 'orange', 'yellow', 'lime', 'green', 'cyan', 'blue', 
                      'mediumorchid', 'violet', 'deeppink']
        
        for r, roi in enumerate(fastremap.unique(label)):
            if roi == 0:
                pass
            else:
                mip_overlay = make_mip(label==roi, concat_axis).astype(np.int16)
                # mask image to just the roi
                index = mip_overlay>0 
                contour_arr = np.zeros(mip_overlay.shape)
                contour_arr[index] = 1

                # plot the contour of the roi
                if should_plot_response:
                    colorOI = colors[roi-1]
                else:
                    colorOI = (colors[r % len(colors)])
                contour = plt.contour(contour_arr, colors=colorOI, linewidths=0.2)

                # annotate the center of the roi with the roi label
                if should_plot_lesion_numbers:
                    c = center_of_mass(contour.allsegs[(-2)][0])
                    plt.annotate((str(roi)), c, color=colorOI, fontsize = 5)

                    c = center_of_mass(contour.allsegs[(-2)][1])
                    plt.annotate((str(roi)), c, color=colorOI, fontsize = 5)

    plt.axis('off')
    plt.savefig(saveFileName, dpi=300, bbox_inches = 'tight', pad_inches = 0)
    plt.close()
    print('Saved MIP: ', subID)


if __name__ == "__main__":
    print('we are plotting lesions and creating MIPs! :)')

    output_dir = '../../ProjectScripts/Australia/output_dir/'
    subject = 'PS001LB_01'

    # load reference image (np.array) for contours.
    img = nrrd.read('../../ProjectScripts/Australia/processed_nrrd_data/PS001LB_01/ctData.nrrd')
    mask_label = nrrd.read('../../ProjectScripts/Australia/processed_nrrd_data/PS001LB_01/mask_44-1.nrrd')
    contour_region = mask_label  # load ground truth contour

    plotAndSaveLesions(output_dir, subject, img[0], mask_label[0], contour_region[0], imtype='CT', should_plot_lesion_numbers=False,
                                       should_plot_response=False,
                                       concat_axis=1)

    print('Done!')
