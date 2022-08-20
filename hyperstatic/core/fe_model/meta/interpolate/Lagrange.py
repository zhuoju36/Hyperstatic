import sympy as syp

l=syp.symbols("l")
xi,eta=syp.symbols("xi eta")

l1=lambda x: 0.5*(1-x)
l2=lambda x: 0.5*(1+x)

#n=2 linear
def N1D():
    N1=l1(xi)
    N2=l2(xi)
    return [N1,N2]

def N2D():
    #n=4 double linear
    N1=l1(xi)*l1(eta)
    N2=l1(xi)*l2(eta)
    N3=l2(xi)*l1(eta)
    N4=l2(xi)*l2(eta)
    return [N1,N2,N3,N4] 