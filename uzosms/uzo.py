# -*- coding: utf-8 -*-
"""
Created on Thu Aug 14 04:56:50 2014

@author: jsousa
"""

import requests
from bs4 import BeautifulSoup
import time
import captcha, train
from path import path

class Uzo(object):
    LOGINURL = "https://www.uzo.pt//pt/meu-uzo/pagina.uzo"
    CAPTCHAURL = "https://meu.uzo.pt/site/gr_captcha-%i.xml"
    SMSURL = 'https://meu.uzo.pt/sms_gratis.xml'
    TEMPFILE = './captcha.jpg'
    MAXCHARS = 137
    
    def __init__(self,username,password):
        """Initializes new Uzo object. Does not login"""
        
        self.username = username
        self.password = password

        self.session = requests.Session()
        self.session.headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64; rv:30.0) Gecko/20100101 Firefox/30.0'        

        self.history = []
        
        self.model = None
        
        self.login()
    
    def checkMessagesLeft(self):
        
        r = self._request(self.SMSURL)
        if r.content:
            soup = BeautifulSoup(r.content)
            summary = soup.find('div',attrs={'class':'summary'})
            if summary:
                nleft,nsent = [int(s.text) for s in summary.findChildren('span',limit=2)]
                return nleft
            elif soup.find('div',attrs={'class':'summary2'}):
                raise UzoError("Can't read number of messages left. Probably not logged in.")
        
        raise UzoError("Can't read number of messages left. Unknown error")
               
    def login(self):

        r = self._request(self.LOGINURL)
        
        #TODO posso verificar aqui logo se o login já está feito
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
        r2 = self._request(self.LOGINURL,'POST',data=data,allow_redirects=False)
        
        if r2.status_code == 302:
            if '?error=' in r2.headers.get('location'):
                raise UzoError('Login failed')
            else:
                return
        
        print "Warning: can't tell login status"
        
    def _grab_captcha(self,fname=None):
        timestamp =  int(time.time()*1000)
               
        r = self._request(self.CAPTCHAURL % timestamp)

        if r.status_code == 200:
            with open(fname or self.TEMPFILE,'wb') as f:
                f.write(r.content)
        else:
            raise UzoError("Can't open captcha")
            
    def _solve_last_captcha(self):
        if not self.model:
            self.model = train.load_model()
            
        im = captcha.load_image(self.TEMPFILE)
        return train.solve_image(im,self.model)

    def send_sms(self,destnumber,msg):
        if len(msg) > self.MAXCHARS:
            print "Max characters: ", self.MAXCHARS
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
        
        r = self._request(self.SMSURL,'POST',data=data)
        if 'sucesso' in r.content:
            return True
        elif 'mensagem excede o máximo de caracteres permitido' in r.content:
            raise UzoError("Message too long")
        else:
            raise UzoError("Failed")
    
   
    def _request(self,url,method='GET',**kwargs):
        print "%s %s" % (method,url)
        if 'GET' == method:
            r = self.session.get(url,**kwargs)
        elif 'POST' == method:
            r = self.session.post(url,**kwargs)
        else:
            raise UzoError('Invalid method %s' % method)
        self.history.append(r)
        return r
    
class UzoError(Exception):
    pass
        
       