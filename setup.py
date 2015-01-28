from setuptools import setup, find_packages

try:
    long_description = open("README.rst").read()
except IOError:
    long_description = ""

setup(
    name="uzosms",
    version="0.1.0",
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
         'path.py',
         'keyring',
         
	],
    entry_points = {
        'console_scripts': [
            'uzo = uzosms.__main__:main'        
        ]
    },
    long_description=long_description
)
