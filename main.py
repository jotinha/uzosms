# -*- coding: utf-8 -*-
"""
Created on Thu Aug 14 04:44:45 2014

@author: jsousa
"""

import uzo 
import captcha, train
from sklearn.externals import joblib

MODEL = joblib.load('model.pkl')


def main_send(loginnumber,password,destnumber,msg,ntries=3):
    s = uzo.login(loginnumber,password)
    ntries = 1    
    for t in range(ntries):    
        train.grab_and_save_captcha(s,'tmp.jpg')
        im = captcha.load_image('tmp.jpg')
        solution = train.solve_image(im,model)
        figure()
        imshow(im)
        show()
        print "Attempting solution: " + solution
        
        resp = uzo.send_sms(destnumber,msg,solution,s)
        
        if 'sucesso' in resp.content:
            print "Enviado"
            return
    
    print "Failed after %i" % ntries
    
        
    
    
    
