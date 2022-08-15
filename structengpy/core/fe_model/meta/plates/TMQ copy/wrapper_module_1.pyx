import numpy as np
cimport numpy as np

cdef extern from 'wrapped_code_1.h':
    void autofunc(double E, double mu, double t, double xi, double eta, double x1, double y1, double x2, double y2, double x3, double y3, double x4, double y4, double *out_8019317812011686532)

def autofunc_c(double E, double mu, double t, double xi, double eta, double x1, double y1, double x2, double y2, double x3, double y3, double x4, double y4):

    cdef np.ndarray[np.double_t, ndim=2] out_8019317812011686532 = np.empty((12,12))
    autofunc(E, mu, t, xi, eta, x1, y1, x2, y2, x3, y3, x4, y4, <double*> out_8019317812011686532.data)
    return out_8019317812011686532