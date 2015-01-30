# -*- coding: utf-8 -*-
"""
Created on Wed Jan 28 15:40:43 2015

@author: jsousa
"""

import sys,os
import keyring
import train
from uzo import Uzo
from path import path

SERVICE = "uzosms"
CONFIG = os.path.expanduser('~/.config/.uzosms')

args = list(reversed(sys.argv))
name = args.pop().split('/')[-1]

usage = """
{0} login <number> <password>    Save login credentials. Must be set before any other command can work
{0} logout                       Delete login credentials
{0} send <number> <msg>          Send sms message to number.
{0} check                        Check number of free messages left
{1}
{0} train                        Re-train model with files from captchas/ folder
{0} grab [n]                     Grab n (default 10) new captchas and save to data folder. 
{1}                              They can be solved manually by changing the .xml files in the 
{1}                              data folder to <solution>.jpg, or by running "{0} solve"
{0} solve                        Launch a gui to manually solve unsolved captchas in data folder
{1}                              (requires matplotlib)
""".format(name,' '*len(name))

def sanitize_phone(phone_str):
    phone_str = phone_str.replace(' ','')
    if phone_str.startswith('+'):
        if not phone_str.startswith('+351'):
            raise Exception('Only works for portuguese numbers')
        else:
            phone_str = phone_str[4:]
    try:
        phone_num = str(int(phone_str))
    except ValueError:
        raise Exception("{0} is not a number".format(phone_str))
    else:
        return phone_num
    
def _delete_credentials():
    login = _load_credentials(skipPassword=True) 
    path(CONFIG).remove_p()
    try:
        keyring.delete_password(SERVICE,login)
    except keyring.errors.PasswordDeleteError:
        pass
    
def _save_credentials(login,password):
    open(CONFIG,'wt').write(login)
    keyring.set_password(SERVICE,login,password)

def _load_credentials(skipPassword=False):
    try:
        login = sanitize_phone(open(CONFIG,'rt').read())
    except IOError:
        raise Exception("No valid login found in {0}\n Must run \"{1} login\" first".format(CONFIG,name))
    if skipPassword:
        return login
        
    password = keyring.get_password(SERVICE,login)
    if password is None:
        raise Exception("No password in keyring\n Must run \"%s login\" first" % login)
    return login,password

# COMMANDS --------------------------------------------------------------------    

def do_login(login,password):
    print "Setting config for ", login
    u = Uzo(login,password)
    _save_credentials(login,password)

def do_logout():
    print "Removing login credentials"
    _delete_credentials()

def do_send(number,message):
    print "Sending sms to", number, "with message :", message
    u = Uzo(*_load_credentials())
    u.send_sms(number,message)
    
def do_check():
    print "Checking number of sms left..."
    u = Uzo(*_load_credentials())
    print u.checkMessagesLeft()

def do_train():
    print "Training model"
    train.train()

def do_grab(n=10):
    print "Grabbing %i new captchas" % n
    u = Uzo(*_load_credentials())
    
    f = lambda i : path(train.DATADIR.joinpath('unsolved_%i.xml' % i))
    i = 0
    for _ in range(n):
        while f(i).exists():
            i+=1
        print "Saving to ", f(i)
        u._grab_captcha(f(i))

def do_solve():
    print "Solving new captchas..."
    train.answer_captchas((train.load_model(),None))
    
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
    
    elif 'solve' == action:
        check_args()
        do_solve()
    
    else:
        raise Exception('Invalid action', action)
    
def main():
    try:
        _main()
    except IndexError:
        print "Usage error!"
        print usage
        
if __name__ == "__main__":
    main()