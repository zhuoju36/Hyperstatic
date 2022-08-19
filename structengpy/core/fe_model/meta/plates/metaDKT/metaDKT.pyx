import numpy as np
cimport numpy as np

cdef extern from 'wrapped_code_0.h':
    void autofunc(double E, double mu, double t, double xi, double eta, double x1, double y1, double x2, double y2, double x3, double y3, double *out_6903487286308824837)

def autofunc_c(double E, double mu, double t, double xi, double eta, double x1, double y1, double x2, double y2, double x3, double y3):

    cdef np.ndarray[np.double_t, ndim=2] out_6903487286308824837 = np.empty((9,9))
    autofunc(E, mu, t, xi, eta, x1, y1, x2, y2, x3, y3, <double*> out_6903487286308824837.data)
    return out_6903487286308824837