# -*- coding: utf-8 -*-
"""
Created on Wed Dec 28 10:41:53 2016

@author: Dell
"""

def assemble(elements):
    """
    Assemble matrix
    Writing the matrix to the disk
    """
    nid = 0
    # Dynamic space allocate
    self.Kmat = np.zeros((len(self.nodes)*6, len(self.nodes)*6))
    self.Mmat = np.zeros((len(self.nodes)*6, len(self.nodes)*6))
    self.Fvec = np.zeros(len(self.nodes)*6)
    self.Dvec = np.zeros(len(self.nodes)*6)

    #Nodal load and displacement, and reset the index
    for node in self.nodes:
        node.id = nid
        load = np.array(node.load)
        self.Fvec[nid * 6: nid * 6 + 6] = np.dot(node.transform_matrix.transpose(),load)
        for i in range(6):
            if node.disp[i] != 0:
                self.Dvec[nid * 6 + i] = node.disp[i]
        nid+=1
        
    nid = 0
    #Beam load and displacement, and reset the index
    for beam in self.beams:
        beam.Id = nid
        i = beam.nodeI.id
        j = beam.nodeJ.id
        T=np.matrix(beam.transform_matrix)
        Tt = T.transpose()

        #Transform matrix
        Vl=np.matrix(beam.localCsys.transform_matrix)
        V=np.zeros((6, 6))
        V[:3,:3] =V[3:,3:]= Vl
        Vt = V.transpose()

        #Static condensation to consider releases
        Kij=sp.bsr_matrix((12, 12))
        Mij=sp.bsr_matrix((12, 12))
        rij=sp.bsr_matrix((12))
        Kij, rij, Mij = beam.StaticCondensation(Kij, rij, Mij)

        #Assemble nodal force vector
        self.Fvec[i*6:i*6+6] += np.dot(Vt,rij[:6])
        self.Fvec[j*6:j*6+6] += np.dot(Vt,rij[6:])

        #Assemble Total Stiffness Matrix
        Ke = np.dot(np.dot(Tt,Kij),T)
        Keii = Ke[:6,:6]
        Keij = Ke[:6,6:]
        Keji = Ke[6:,:6]
        Kejj = Ke[6:,6:]
        self.Kmat[i*6:i*6+6, i*6:i*6+6] += Keii
        self.Kmat[i*6:i*6+6, j*6:j*6+6] += Keij
        self.Kmat[j*6:j*6+6, i*6:i*6+6] += Keji
        self.Kmat[j*6:j*6+6, j*6:j*6+6] += Kejj

        #Assembel Mass Matrix        
        Me = np.dot(np.dot(Tt,Mij),T)
        Meii = Me[:6,:6]
        Meij = Me[:6,6:]
        Meji = Me[6:,:6]
        Mejj = Me[6:,6:]
        self.Mmat[i*6:i*6+6, i*6:i*6+6] += Meii
        self.Mmat[i*6:i*6+6, j*6:j*6+6] += Meij
        self.Mmat[j*6:j*6+6, i*6:i*6+6] += Meji
        self.Mmat[j*6:j*6+6, j*6:j*6+6] += Mejj
        nid+=1

    