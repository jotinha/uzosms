# -*- coding: utf-8 -*-
"""
Created on Mon Aug  4 21:28:37 2014

@author: jsousa
"""
from scipy import ndimage,misc
from numpy import where,array,polyfit,polyval,zeros,ones,unique,sum,polyfit,polyval, \
                  arccos,dot,sqrt,pi,isnan
                  
import numpy as np

def transform_image(im,threshold=220):
    return where(im < threshold,1,0)    
    
def load_image(fname,threshold = 220):
    """
    opens image file with name fname and returns an image 2D array where
    active pixels have value 1 and non-active value 0
    """
    im = ndimage.imread(fname,flatten=True)
    im = transform_image(im,threshold=threshold)
    return im

def image_analysis(im):
    """TEMP"""
    #attempt to get baselines
    h,w = im.shape
    
    def _getFirstBlack(col):
        for i in xrange(len(col)):
            if col[i] == 0:
                return i
        return NaN
            
    upline = array([h-_getFirstBlack(col[::-1]) for col in im.T])
    dnline = array([_getFirstBlack(col) for col in im.T])
    #plot(upline)
    #plot(dnline)
    
    center = array([r_[:w][col==0].mean() for col in im.T])
    idxs = where(center == center)[0] #not nan
    y = center[idxs]
    x = r_[:w][idxs]
    p = polyfit(x,y,3)
#    figure()
    #imshow(im)
    #plot(x,polyval(p,x))

def get_continuous_regions(im,activeValue=1,min_pixels = 0):
    h,w = im.shape   
   
    def neighbors(pos):
        i,j = pos
        for jj in (j-1,j,j+1):
            for ii in (i-1,i,i+1):
                if (0 <= ii < h) and (0 <= jj < w) and (ii,jj) != (i,j):
                    yield ii,jj

    im_class = zeros(im.shape)

    i,j = 0,0
    while True:
        pos = i,j
        if im[pos] == activeValue:
            c = 0
            for n in neighbors(pos):
                if im_class[n] != 0:
                    c = im_class[n]
                    break
    
            if c is 0:
                c = im_class.max() + 1
        
            im_class[pos] = c
            for n in neighbors(pos):
                if im_class[n] != 0:
                    im_class[im_class == im_class[n]] = c
    
        if j == w - 1:
            if i == h-1:
                break
        
            j = 0
            i += 1
        else:
            j += 1
    
    #renumber classes and check they they have minimum number of pixels
    c = 0
    for oldc in sorted(unique(im_class)):
        if oldc != 0:
            idxs = im_class == oldc        
            if idxs.sum() >= min_pixels:
                c += 1
                im_class[idxs] = c
            else:
                im_class[idxs] = 0
    
    return im_class

def unrotate_char(char):
    #calculate center of mass in the x diretion (one for each row)
    
    cmx = array([
        sum(x*m for x,m in enumerate(row)) for row in char]) / char.sum(1)

    h = where(~isnan(cmx))[0]
    cmx = cmx[h]

    pol = polyfit(h,cmx,1)
    x0 = polyval(pol,0)
    x1 = polyval(pol,1)
    vec = [x1-x0,1]
#    figure()
#    subplot(1,2,1)
#    imshow(char)
#    plot(cmx,h,'b-')
#    plot(polyval(pol,[0,char.shape[0]]),[0,char.shape[0]],'r-')
    
    #now get angle of line relative to y-axis
    #angle = np.arccos( np.dot(vec,[0,1]))
    angle = arccos(dot([0,1],vec) / sqrt(vec[0]**2 + vec[1]**2))
    angle = (1 if vec[0] < 0 else -1) * angle*180/pi    
#    subplot(1,2,2)
    char2 = ndimage.rotate(char,angle)
#    imshow(char2)

    return char2
#split into continguous pixel regions ----------------------
def get_chars(im,min_pixels = 50,nchars=6):

    im_class = get_continuous_regions(im,min_pixels = min_pixels,activeValue=1)
       
    #split into characters ---
    chars = {}
    norm_size = 16
    for c in unique(im_class):
        if c==0: continue
        
        #get character mask
        char = where(im_class == c,1,0)        
        
        assert char.sum() >= min_pixels
        
        cim = misc.toimage(char,high=1,low=0)

        #tight crop
        box = cim.getbbox()
        cim = cim.crop(box)        
        
        #rotate
        cim = misc.toimage(unrotate_char(array(cim)))
        
      

        #crop into square and center character
        x0,y0,x1,y1 = cim.getbbox() #this is a new box, different from previous
        cw = x1-x0
        ch = y1-y0
        half = max(cw,ch)/2
        cmx = (x0+x1)/2
        cmy = (y0+y1)/2
        
        cim = cim.crop((cmx-half,cmy-half,cmx+half,cmy+half))
        #resize
        cim = cim.resize((norm_size,norm_size))
#        figure()
#        imshow(cim)
                
        #imshow(char_norm)    
        chars[box[0]] = array(cim)
    
    #make ordered list from dict
    chars = [chars[left] for left in sorted(chars.keys())]
    if len(chars) != nchars:
        print "Warning: Got %i chars, expected %i" % (len(chars),nchars)
        
    return chars

def get_number_holes(char):
    #add a border of zeros around char
    h,w = char.shape
    c = zeros((h+2,w+2))
    c[1:-1,1:-1] = char
    
    #count number of holes by calculating the number of continuous regions
    #with pixel value 0. We remove -2 because we have to remove the symbol region
    #only one, and the outside area (also only one)
    n_holes = len(unique(get_continuous_regions(c,activeValue=0,min_pixels=3))) - 2
    return n_holes

