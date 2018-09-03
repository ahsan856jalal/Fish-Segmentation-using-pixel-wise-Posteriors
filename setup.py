from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

ext_modules=[
    Extension("pixcel",
              ["pixcel.pyx"],
              libraries=["m"]) # Unix-like specific
]

setup(
  name = "Cython Magic",
  cmdclass = {"build_ext": build_ext},
  ext_modules = ext_modules
)
