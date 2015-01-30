# -*- coding: utf-8 -*-
"""
Created on Wed Aug  6 17:01:02 2014

@author: jsousa
"""
from path import path

from captcha import *
import sklearn
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn import svm
from sklearn.externals import joblib

MODELFILE = path(__file__).dirname().joinpath('model.pkl')
            
DATADIR = path(__file__).dirname().joinpath('captchas')

print "DATADIR:",DATADIR          
          
def grab_and_save_captcha(session,fname=None):
    r = grab_captcha(session)
    if r.status_code == 200 and r.content:
        if fname is None: 
            fname = DATADIR + r.url.split('/')[-1]
        with open(fname, 'wb') as f:
            f.write(r.content)
    else:
        raise SystemError, "Invalid response"

def download_captchas(n=10,max_interval=10):
    s = login()
    for i in xrange(n):
        print i
        time.sleep(rand()*max_interval)
        grab_and_save_captcha(s)
        
def answer_captchas(lr_pca=None):
    for fname in path(DATADIR).files('*.xml'):
        im = load_image(fname)
        imshow(im)
        show()
        if lr_pca:
            suggestion = ''.join(map(str,
                            solve_chars(get_chars(im),lr_pca[0],lr_pca[1])))
            print "suggestion: ", suggestion
        answer = raw_input('Answer: ')
        if not answer.strip():
            answer = suggestion
        elif answer.strip().lower() == 'q':
            break

        fname.move('%s/%s.jpg' % (DATADIR,answer))

def create_chars_train():
    charsTrain = {i:[] for i in xrange(10)}
    charsTrain_fname = {i:[] for i in xrange(10)}
    for fname in path(DATADIR).files('*.jpg'):
        numbers = map(int,fname.basename().stripext())
        
        im = load_image(fname)
        chars = get_chars(im)
        if len(chars) != 6:
            print "get_chars failed for %s" % fname
            continue
        
        for number,char in zip(numbers,chars):
            charsTrain[number].append(char)
            charsTrain_fname[number].append(fname)

    return charsTrain,charsTrain_fname


def char_to_featvector(char):
    return char.flatten()
#    return np.append(get_number_holes(char),char.flatten())

def create_training_set():
    charsTrain = create_chars_train()[0]           
    X = []
    Y = []
    for number,chars in charsTrain.iteritems():
        for char in chars:
            X.append(char_to_featvector(char))
            Y.append(number)
    X = array(X)
    Y = array(Y)
    return X,Y
    
def test_holes():
    charsTrain,charsTrain_fname = create_chars_train()
    expected_number = [1,0,0,0,1,0,1,0,2,1]
    for n in xrange(10):
        for char,fname in zip(charsTrain[n],charsTrain_fname[n]):
            nholes = get_number_holes(char)
            if nholes != expected_number[n]:
                figure()
                imshow(char)
                show()
                print fname
                print "Expecting number %i but got %i holes" % (n,nholes)

def fit(X,Y,reduce_dims = None,**kw):
#    X_corr = sklearn.decomposition.PCA(n_components= reduce_dims).fit_transform(X[:,1:])
#    X = X[:,:X_corr.shape[1]+1]
#    X[:,1:] = X_corr
    if reduce_dims:
        pca = PCA(n_components= reduce_dims).fit(X)
        X = pca.transform(X)
    else:
        pca = None

    X_train,X_test,Y_train,Y_test = sklearn.cross_validation.train_test_split(X,Y)
#    X_train,Y_train = X,Y
    model = svm.SVC(kernel='linear',**kw).fit(X_train,Y_train)
#    model = RandomForestClassifier(n_estimators=50)

#    model = tree.DecisionTreeClassifier(**kw)

#    model = LogisticRegression(**kw)
    model.fit(X_train,Y_train)
    print "Score:", model.score(X_test,Y_test)
    return model,pca

def solve_chars(chars,lr,pca=None):
    X_eval = array(map(char_to_featvector,chars))
    if pca:
        X_eval = pca.transform(X_eval)
    return lr.predict(X_eval)

def solve_image(im,lr,pca=None,as_str = True):
    r = solve_chars(get_chars(im),lr,pca)
    if as_str:
        r = ''.join(map(str,r))
    return r

def save_model(model,pca=None):
    joblib.dump(model,MODELFILE,compress=9)
    if pca:
        raise NotImplementedError

def load_model():
    return joblib.load(MODELFILE)    

def train():
    X,Y = create_training_set()
    model,pca = fit(X,Y)
    save_model(model,pca)
    