from distutils.core import setup
from Cython.Build import cythonize

setup(
	name = "pybgs",
	include_dirs = ['/usr/local/include/opencv/', '/usr/local/include/opencv2/core', '/usr/local/include/opencv2/highgui','~/.virtualenvs/cv/lib/python3.5/site-packages/numpy/core/include'],
    ext_modules = cythonize('pybgs.pyx')
)

