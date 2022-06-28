from setuptools import setup
from setuptools import find_packages

<<<<<<< HEAD
VERSION = '0.1.11'
=======

VERSION = '0.1.12'
>>>>>>> 01a10ef3699b5dfa5af6611afddaa149cb9f5fff

setup(
    name='StructEngPy', 
    version=VERSION, 
    author='Zhuoju Huang',
    author_email='zhuoju36@hotmail.com',
    license='MIT',
    description='package for structural engineering', 
    packages=find_packages(),
    zip_safe=False,
    python_requires=">=3.6",
    install_requires=[
        'numpy>=1.21',
        'scipy>=1.7',
<<<<<<< HEAD
        'quadpy>=0.16',
=======
        'quadpy>=0.16'
>>>>>>> 01a10ef3699b5dfa5af6611afddaa149cb9f5fff
    ],
)