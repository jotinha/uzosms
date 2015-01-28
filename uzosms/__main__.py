# -*- coding: utf-8 -*-
"""
Created on Wed Jan 28 15:40:43 2015

@author: jsousa
"""

import sys,os
import keyring

SERVICE = "uzosms"
CONFIG = os.path.expanduser('~/.config/.uzosms')

args = list(reversed(sys.argv))
name = args.pop().split('/')[-1]

usage = """
{0} login <number> <password>    Save login credentials. Must be set before any other command can work
{0} logout                       Delete login credentials
{0} send <number> <msg>          Send sms message to number.
{0} check                        Check number of free messages left
{0} train                        Re-train model with files from captchas/ folder
{0} grab [n]                     Grab n (default 10) new captchas and save to data folder. 
                                 They must be solved by manually renaming <timestamp>.xml to <solution>.jpg
""".format(name)

def sanitize_phone(phone_str):
    phone_str = phone_str.replace(' ','')
    if phone_str.startswith('+'):
        if not phone_str.startswith('+351'):
            raise Exception('Only works for portuguese numbers')
        else:
            phone_str = phone_str[4:]
    try:
        phone_num = int(phone_str)
    except ValueError:
        raise Exception("{0} is not a number".format(phone))
    else:
        return phone_num
        
def _load_login():
    try:
        return sanitize_phone(open(CONFIG,'rt').read())
    except IOError:
        raise Exception("No valid login found in {0}\n Run \"{1} login\" first".format(CONFIG,name))
        
def _save_login(login):
    open(CONFIG,'wt').write(login)

def do_login(login,password):
    print "Setting config for ", login
    keyring.set_password(SERVICE,str(login),password)
    _save_login(str(login))

def do_logout():
    print "Removing login credentials"
    login = _load_login()
    if login:
        keyring.delete_password(SERVICE,str(login))

def do_send(number,message):
    print "Sending sms to", number, "with message :", message

def do_check():
    print "Checking number of sms left..."

def do_train():
    print "Training model"

def do_grab(n=10):
    print "Grabbing %i new captchas" % n
    
def _main():
    global args
    def check_args():
        if len(args) > 0:
            raise Exception('Too many arguments')
    
    action = args.pop().lower()
    
    if 'login' == action:
        login    = sanitize_phone(args.pop())
        password = args.pop()
        check_args()
        do_login(login,password)
    
    elif 'logout' == action:
        check_args()
        do_logout()
    
    elif 'send' == action:
        number = sanitize_phone(args.pop())
        
        message = ' '.join(reversed(args)).strip() #consumes all remaining arguments
        args = []
        check_args()
        do_send(number,message)
    
    elif 'check' == action:
        check_args()
        do_check()
    
    elif 'train' == action:
        check_args()
        do_train()
    
    elif 'grab' == action:
        check_args()
        do_grab(int(args.pop())) if len(args) > 0 else do_grab()
    
    else:
        raise Exception('Invalid action', action)
    
def main():
    try:
        _main()
    except Exception as e:
        print "Usage error!", e
        print usage
        
if __name__ == "__main__":
    main()