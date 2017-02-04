from setuptools import setup, find_packages

try:
    long_description = open("README.rst").read()
except IOError:
    long_description = ""

setup(
    name="uzosms",
    version="0.1.1",
    description="send sms with uzo.pt bypassing the captcha",
    license="MIT",
    author="jotinha",
    packages=find_packages(),
    install_requires=[
	    'requests',
         'beautifulsoup4',
         'numpy',
         'scipy',
         'scikit-learn',
         'pillow',
         'path.py',
         'keyring',
         'nose',
         
	],
    entry_points = {
        'console_scripts': [
            'uzo = uzosms.__main__:main'        
        ]
    },
    package_data = {
         'uzosms': ['captchas/*','model.pkl']   
    },
    long_description=long_description
)
