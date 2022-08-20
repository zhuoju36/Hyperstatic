import sympy as syp

l=syp.symbols("l")
xi,eta=syp.symbols("xi eta")

#H0 H1 is the order of the function in 0,1
H01=lambda x:1-3*x**2+2*x**3
H02=lambda x:(x-2*x**2+x**3)*l
H11=lambda x:3*x**2-2*x**3
H12=lambda x:(x**3-x**2)*l

#linear 
def N1D():
    N1=H01(xi)
    N2=H02(xi)
    N3=H11(xi)
    N4=H12(xi)
    return [N1,N2,N3,N4]

#double linear
def N2D():
    N1=H01(xi)*H01(eta)
    N2=H11(xi)*H01(eta)
    N3=H01(xi)*H11(eta)
    N4=H11(xi)*H11(eta)
    N5=H02(xi)*H01(eta)
    N6=H12(xi)*H01(eta)
    N7=H02(xi)*H11(eta)
    N8=H12(xi)*H11(eta)
    N9=H01(xi)*H02(eta)
    N10=H11(xi)*H02(eta)
    N11=H01(xi)*H12(eta)
    N12=H11(xi)*H12(eta)
    N13=H02(xi)*H02(eta)
    N14=H12(xi)*H02(eta)
    N15=H02(xi)*H12(eta)
    N16=H12(xi)*H12(eta)
    return [N1,N2,N3,N4,
            N5,N6,N7,N8,
            N9,N10,N11,N12,
            N13,N14,N15,N16,]
