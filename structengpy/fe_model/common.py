# -*- coding: utf-8 -*-
class Tolerance(object):
    __abs_tol = 1e-9
    __rel_tol = 1e-6

    @classmethod
    def abs_tol(cls):
        return cls.__abs_tol

    @classmethod
    def rel_tol(cls):
        return cls.__rel_tol

    @classmethod
    def set_abs_tol(cls,val):
        cls.__abs_tol=val

    @classmethod
    def set_rel_tol(cls,val):
        cls.__rel_tol=val

if __name__ == '__main__':
    Tolerance.set_abs_tol(42)
    print(Tolerance.abs_tol())