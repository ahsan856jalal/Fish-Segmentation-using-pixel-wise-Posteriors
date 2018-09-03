import numpy as np
cimport numpy as np
cimport cython
import ctypes
from cpython cimport array

cdef extern from "pixcel.h":
    void _applyModel(unsigned char image[], unsigned char output[], int f[], int height, int width)

@cython.boundscheck(False)
@cython.wraparound(False)
def applyModel(np.ndarray [unsigned char, ndim=3] image,np.ndarray [unsigned char, ndim=2] mask, np.ndarray [int, ndim=3] f):

    cdef int height, width
    height, width = image.shape[0:2]

    #cdef array.array im_array = array.array('i', image.flat)
    #cdef array.array mask_array = array.array('i', mask.flat)
    #cdef array.array f_array = array.array('i', f.flat)
    
    cdef np.ndarray[unsigned char, ndim=1, mode='c'] _image = np.ascontiguousarray(image.flat)
    cdef np.ndarray[unsigned char, ndim=1, mode='c'] _mask = np.ascontiguousarray(mask.flat)
    cdef np.ndarray[int, ndim=1, mode='c'] _f = np.ascontiguousarray(f.flat)

    #_applyModel(im_array.data.as_ints, mask_array.data.as_ints, height, width, f_array.data.as_ints)
    _applyModel(&_image[0], &_mask[0], &_f[0], height, width)

    return np.uint8(_mask).reshape((height, width))

cdef extern from "pixcel.h":
    void _computePosteriors(unsigned char image[], unsigned char mask[], int f[], int height, int width)

@cython.boundscheck(False)
@cython.wraparound(False)
def computePosteriors(np.ndarray [unsigned char, ndim=3] image, np.ndarray [unsigned char, ndim=2] mask):
    
    cdef int height, width
    height, width = image.shape[0:2]
    
    cdef np.ndarray[unsigned char, ndim=1, mode='c'] _image = np.ascontiguousarray(image.flat)
    cdef np.ndarray[unsigned char, ndim=1, mode='c'] _mask = np.ascontiguousarray(mask.flat)
    cdef np.ndarray[int, ndim=1, mode='c'] _f = np.ascontiguousarray(np.zeros((32, 32, 32), dtype=np.int32).flat)
    
    _computePosteriors(&_image[0], &_mask[0], &_f[0], height, width)

    return np.int32(_f).reshape((32, 32, 32))

cdef extern from "pixcel.h":
    void _pwp(unsigned char image[], unsigned char mask[], int f[], int height, int width, int bits)

@cython.boundscheck(False)
@cython.wraparound(False)
def pixcelWisePosteriors(np.ndarray [unsigned char, ndim=3] image,np.ndarray [unsigned char, ndim=2] mask, int bits = 5):
    cdef int height, width
    height, width = image.shape[0:2]
    
    #cdef array.array im_array = array.array('i', image.flat)
    #cdef array.array mask_array = array.array('i', mask.flat)
    
    cdef np.ndarray[int, ndim=1, mode='c'] _f = np.ascontiguousarray(np.zeros((32, 32, 32), dtype=np.int32).flat)
    cdef np.ndarray[unsigned char, ndim=1, mode='c'] _image = np.ascontiguousarray(image.flat)
    cdef np.ndarray[unsigned char, ndim=1, mode='c'] _mask = np.ascontiguousarray(mask.flat)
    
    #_pwp(im_array.data.as_ints, mask_array.data.as_ints, height, width, bits)
    _pwp(&_image[0], &_mask[0], &_f[0], height, width, bits)
    return np.uint8(_mask).reshape((height, width))
