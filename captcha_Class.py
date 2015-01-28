# -*- coding: utf-8 -*-
"""
Created on Thu Aug 14 03:51:06 2014

@author: jsousa
"""

                  

class Char(object):
    
    def __init__(self,captcha,char_pil,char_box,threshold=30):
        self.captcha = captcha
        self.char_pil = char_pil
        self.char_box = char_box

    def unrotate(self):
   
        char = array(self.char_pil)

        #calculate center of mass in the x diretion (one for each row)   
        cmx = array([
            sum(x*m for x,m in enumerate(row)) for row in char]) / char.sum(1)
    
        h = where(~np.isnan(cmx))[0]
        cmx = cmx[h]
    
        pol = polyfit(h,cmx,1)
        x0 = polyval(pol,0)
        x1 = polyval(pol,1)
        vec = [x1-x0,1]
    
        figure()
        imshow(char)
        plot(cmx,h,'b-')
        plot(np.polyval(pol,[0,char.shape[0]]),[0,char.shape[0]],'r-')
        
        #now get angle of line relative to y-axis
        #angle = np.arccos( np.dot(vec,[0,1]))
        angle = arccos(dot([0,1],vec) / sqrt(vec[0]**2 + vec[1]**2))
        self.angle = (1 if vec[0] < 0 else -1) * angle*180/pi
        print self.angle
        self.char_pil_original = self.char_pil
        
        char_rotated = self.char_pil.rotate(self.angle,resample=Image.BICUBIC,expand=True)
        
        char_rotated = char_rotated.crop(char_rotated.getbbox())
        
        self.char_pil= char_rotated

        return self.char_pil
    
    def resize(self,norm_size=10):
        cim = self.char_pil
        #crop into square and center character
        x0,y0,x1,y1 = cim.getbbox() 
        cw = x1-x0
        ch = y1-y0
        half = max(cw,ch)/2
        cmx = (x0+x1)/2
        cmy = (y0+y1)/2
        
        cim = cim.crop((cmx-half,cmy-half,cmx+half,cmy+half))
        #resize
        cim = cim.resize((norm_size,norm_size))
        self.char_pil = cim
        return cim
        
    
class Captcha(object):

    def __init__(self,fname,threshold=220):
        self.im_original = ndimage.imread(fname,flatten=True)
        self.im_simple = where(self.im_original < threshold,1,0)    
        self.im_original = 255-self.im_original  #invert
        self.im_pil = misc.toimage(self.im_original)
        
        self.get_chars()
        
    def get_chars(self,min_pixels=50,nchars=6):
        im = self.im_simple
        self.im_class = im_class = get_continuous_regions(im,min_pixels = min_pixels,activeValue=1)
        
        chars = {}
        for c in unique(im_class):
            if c==0: continue
            
            #get character mask
            mask = where(im_class == c,1,0)        
            
            assert mask.sum() >= min_pixels
            
            mask_pil = misc.toimage(mask,high=1,low=0)
    
            char_box = mask_pil.getbbox()
            
            char_pil = misc.toimage(
                where(mask,self.im_original,0)).crop(char_box)
            
            chars[char_box[0]] = Char(self,char_pil,char_box)
       
        #make ordered list from dict
        self.chars = [chars[left] for left in sorted(chars.keys())]
        if len(self.chars) != nchars:
            print "Warning: Got %i chars, expected %i" % (len(self.chars),nchars)
    
        return self.chars
    
    def unrotate_chars(self):
        im_class = self.im_class
        
        for bbox in self.bboxes:
            figure()
            subplot(1,2,1)
            char = unrotate_char(self.im_pil.crop(bbox),True)
            subplot(1,2,2)            
#            figure()
            
            imshow(255-array(char))
   