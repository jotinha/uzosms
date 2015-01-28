# -*- coding: utf-8 -*-
"""
Created on Thu Aug 14 04:56:50 2014

@author: jsousa
"""

import requests
from BeautifulSoup import BeautifulSoup
import time
import captcha, train

MODEL = train.MODEL

class Uzo(object):
    LOGINURL = "https://www.uzo.pt//pt/meu-uzo/pagina.uzo"
    CAPTCHAURL = "https://meu.uzo.pt/site/gr_captcha-%i.xml"
    SMSURL = 'https://meu.uzo.pt/sms_gratis.xml'
    TEMPFILE = './captcha.jpg'
    
    def __init__(self,username,password):
        self.username = username
        self.password = password
        
        self.session = requests.Session()
        self.session.headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64; rv:30.0) Gecko/20100101 Firefox/30.0'        
        
        self.login()

    def login(self):
        
        self.last_response = r = self.session.get(self.LOGINURL)
   
        soup = BeautifulSoup(r.content)
    
        #find first form in the page, the login form    
        form = soup.find('form')
        
        #copy all form fields because they are apparently important
        data = {}
        for inp in form.findAll('input'):
            attrs = dict(inp.attrs)
            name = attrs['name']
            if name:
                value = attrs['value'] if 'value' in attrs else ''
                data[name] = value
        
        #add these fields
        data['ctl00$ctl00$ucLogin1$txbUsername'] = self.username
        data['ctl00$ctl00$ucLogin1$txbPassword'] = self.password
        data['__EVENTTARGET'] = 'ctl00$ctl00$ucLogin1$lnkbtnOK'
        
        #post form
    
        self.last_response = r2 = self.session.post(self.LOGINURL,data=data)
    
        if 'Entrou na UZO' in r2.content:
            return True
        else:
            raise UzoError("Login failed")
    
    def _grab_captcha(self,fname=None):
        timestamp =  int(time.time()*1000)
               
        self.last_response = r = self.session.get(self.CAPTCHAURL % timestamp)

        if r.status_code == 200:
            with open(fname or self.TEMPFILE,'wb') as f:
                f.write(r.content)
        else:
            raise UzoError("Can't open captcha")
            
    def _solve_last_captcha(self):
        im = captcha.load_image(self.TEMPFILE)
        return train.solve_image(im,MODEL)

    def send_sms(self,destnumber,msg):
        if len(msg) > 137:
            print "Max characters: 137"
            return            
            
        c = self._grab_captcha()
        solution = self._solve_last_captcha()
        
        data = {
            'sms_type':'2',
            'sms_tax': '0',
            'sendSMS': 'on',
            'ntelemovel': destnumber,
            'message':msg,
            'captcha':solution,
        }
        
        self.last_response = r = self.session.post(self.SMSURL,data=data)
        if 'sucesso' in r.content:
            return True
        elif 'mensagem excede o máximo de caracteres permitido' in r.content:
            raise UzoError("Message too long")
        else:
            raise UzoError("Failed")
            
    
class UzoError(Exception):
    pass
        
       