import os
try:
    from setuptools import setup
    from setuptools import find_packages
    from setuptools import Extension
except ImportError:
    from distutils.core import setup
    from distutils.extension import Extension
from Cython.Build import cythonize,build_ext
from Cython.Distutils import build_ext

cy_opts = {}
import numpy as np

VERSION = '0.2.0'

elm_path=os.path.dirname(os.path.realpath(__file__))
elm_path=os.path.join(elm_path,'hyperstatic')
elm_path=os.path.join(elm_path,'core')
elm_path=os.path.join(elm_path,'fe_model')
elm_path=os.path.join(elm_path,'meta')

ext_mods = [
    Extension('metaT9', [ 
        os.path.join(elm_path,'membranes','T9','metaT9.pyx'), 
        os.path.join(elm_path,'membranes','T9','wrapped_code_0.c')
        ],
    include_dirs=[np.get_include()],
    library_dirs=[],
    libraries=[],
    extra_compile_args=['-std=c99'],
    extra_link_args=[]
    ),
    Extension('metaGQ12', [ 
        os.path.join(elm_path,'membranes','GQ12','metaGQ12.pyx'), 
        os.path.join(elm_path,'membranes','GQ12','wrapped_code_0.c')
        ],
    include_dirs=[np.get_include()],
    library_dirs=[],
    libraries=[],
    extra_compile_args=['-std=c99'],
    extra_link_args=[]
    ),
    Extension('metaDKT', [ 
        os.path.join(elm_path,'plates','metaDKT','metaDKT.pyx'), 
        os.path.join(elm_path,'plates','metaDKT','wrapped_code_0.c')
        ],
    include_dirs=[np.get_include()],
    library_dirs=[],
    libraries=[],
    extra_compile_args=['-std=c99'],
    extra_link_args=[]
    ),
    Extension('metaDKQ', [ 
        os.path.join(elm_path,'plates','metaDKQ','metaDKQ.pyx'), 
        os.path.join(elm_path,'plates','metaDKQ','wrapped_code_0.c')
        ],
    include_dirs=[np.get_include()],
    library_dirs=[],
    libraries=[],
    extra_compile_args=['-std=c99'],
    extra_link_args=[]
    ),
    Extension('metaTMQb', [ 
        os.path.join(elm_path,'plates','TMQ','metaTMQb.pyx'), 
        os.path.join(elm_path,'plates','TMQ','wrapped_code_0.c')
        ],
    include_dirs=[np.get_include()],
    library_dirs=[],
    libraries=[],
    extra_compile_args=['-std=c99'],
    extra_link_args=[]
    ),
    Extension('metaTMQs', [ 
        os.path.join(elm_path,'plates','TMQ','metaTMQs.pyx'), 
        os.path.join(elm_path,'plates','TMQ','wrapped_code_1.c')
        ],
    include_dirs=[np.get_include()],
    library_dirs=[],
    libraries=[],
    extra_compile_args=['-std=c99'],
    extra_link_args=[]
    ),
]

setup(
    name='Hyperstatic', 
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
        'quadpy>=0.16',
        'vedo>=2022.2.3',
        'cython>=0.29'
    ],
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Manufacturing',
        'Topic :: Education',
        'Topic :: Scientific/Engineering',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    url='https://github.com/zhuoju36/Hyperstatic',
    cmdclass={'build_ext': build_ext},
    ext_modules=cythonize(ext_mods, **cy_opts),
)