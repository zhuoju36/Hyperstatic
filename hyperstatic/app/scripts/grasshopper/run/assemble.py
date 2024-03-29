from ghpythonlib.componentbase import executingcomponent as component
import Grasshopper, GhPython
import System
import Rhino
import rhinoscriptsyntax as rs
import os
import subprocess

class MyComponent(component):
    
    def RunScript(self, path, py_path, force_unit,tol, node_loads, node_restraints, beams, run):
        """Assemble the objects for Hyperstatic.
            Inputs:
                path: (str) working path.
                py_path: (str) path of python executable.
                force_unit: (str) N,kN.
                tol: (float) merge tolerance
                node_loads: node load object
                node_restraints: restraints object.
                beams: beams object.

                run: (bool) run the script or not.
            Output:
                output: output info
                model: assembled model object."""
                                        
        __author__ = "Zhuoju Huang"
        __version__ = "2022.07.12"
                                        
        doc=Rhino.RhinoDoc.ActiveDoc
        scale=1
        fscale=1
        if str(doc.ModelUnitSystem)=="Millimeters":
            scale=0.001
        elif str(doc.ModelUnitSystem)=="Meters":
            scale=1
        else:
            raise Exception("unit must only be Millimeters or Meters.") 
        if force_unit.upper()=="N":
            fscale=1
        elif force_unit.upper()=="KN":
            fscale=0.001
        else:
            raise Exception("force_unit must only be N or kN.") 
        self.scale=scale
        self.fscale=fscale
            
        class Model(object):
            def __init__(self,path,py_path):
                self.path=path
                self.py_path=py_path
                self.nodes=[]
                self.beams=[]
                        
        class Node(object):
            def __init__(self,name, pt):
                self.name=name
                self.point=pt
                        
        output="Not yet run."
        model=None
                        
        if run==True:
            model=Model(path,py_path)
            vertices=[]
            conn={}
            c=[]
            nodes=[]
            def find_pt(pt,lst,tol=1e-3):
                loc=-1
                for _i in range(len(lst)):
                    if pt.DistanceTo(lst[_i].point)<tol:
                        loc=_i
                        break
                return loc
                            
            # analyze material and sections:
            sections={}
            materials={}
            for beam in beams:
                name=id(beam.section)
                sections[name]=beam.section
                
            for section in sections.values():
                name=id(section.material)
                materials[name]=section.material
                
            # special nodes first
            for snode in node_restraints+node_loads:
                loc=find_pt(snode.node.point,nodes,tol)
                if loc==-1:
                    nodes.append(snode.node)
                else:
                    snode.node=nodes[loc]
                                                    
            # generate general node
            for b in beams:
                _c=b.curve
                pt1=_c.PointAtStart
                pt2=_c.PointAtEnd
                loc1=find_pt(pt1,nodes,tol)
                loc2=find_pt(pt2,nodes,tol)
                bname=b.name
                conn[bname]=[loc1,loc2]
                if loc1==-1:
                    loc1=len(nodes)
                    node=Node("gen_%d"%loc1,pt1)
                    conn[bname][0]=loc1
                    nodes.append(node)
                if loc2==-1:
                    loc2=len(nodes)
                    node=Node("gen_%d"%loc2,pt2)
                    nodes.append(node)
                    conn[bname][1]=loc2
            model.nodes=nodes
            model.beams=conn
            model.sections=sections
            model.materials=materials
            # write script
            if not os.path.exists(path):
                os.mkdir(path)
            file=os.path.join(path,"gen_assemble.py")
            
            
            with open(file, "w+") as f:
                [f.write("#") for i in range(62)]
                f.write("\n")
                f.write("# This script is generate by Grasshopper app of Hyperstatic. #\n")
                [f.write("#") for i in range(62)]
                f.write("\n")
                f.write("from hyperstatic.core import Api\n")
                f.write("\n")
                f.write("api=Api(r'%s')\n"%path)
                f.write("\n")
                
                for material in model.materials.values():
                    f.write('api.add_isotropic_material("%s",%f,%f,%f,%f)\n'%(
                        material.name,
                        material.rho/scale**3,
                        material.E*fscale/scale**2,
                        material.mu,
                        material.a,))
                for section in model.sections.values():
                    if section.shape=="general":
                        f.write('api.add_beam_section_general("%s","%s",%f,%f,%f,%f,%f,%f,%f,%f)\n'%(
                            section.name,
                            section.material.name,
                            section.A*scale**2,
                            section.As2*scale**2,
                            section.As3*scale**2,
                            section.I2*scale**4,
                            section.I3*scale**4,
                            section.J*scale**4,
                            0,0)) #no W22,W33 now
                    elif section.shape=="I":
                        f.write('api.add_beam_section_I("%s","%s",%f,%f,%f,%f)\n'%(
                            section.name,
                            section.material.name,
                            section.h*scale,
                            section.b*scale,
                            section.tw*scale,
                            section.tf*scale))
                    elif section.shape=="rectangle":
                        f.write('api.add_beam_section_rectangle("%s","%s",%f,%f)\n'%(
                            section.name,
                            section.material.name,
                            section.h*scale,
                            section.b*scale))
                    elif section.shape=="I":
                        f.write('api.add_beam_section_box("%s","%s",%f,%f,%f,%f)\n'%(
                            section.name,
                            section.material.name,
                            section.h*scale,
                            section.b*scale,
                            section.tw*scale,
                            section.tf*scale))
                    elif section.shape=="circle":
                        f.write('api.add_beam_section_I("%s","%s",%f)\n'%(
                            section.name,
                            section.material.name,
                            section.d*scale))
                    elif section.shape=="pipe":
                        f.write('api.add_beam_section_I("%s","%s",%f,%f)\n'%(
                            section.name,
                            section.material.name,
                            section.d*scale,
                            section.t*scale))
                    else:
                        raise Exception("Error when adding beam section")
                for node in nodes:
                    name=node.name
                    pt=node.point
                    f.write('api.add_node("%s",%f,%f,%f)\n'%(name,
                        pt.X*scale,pt.Y*scale,pt.Z*scale))
                
                for beam in beams:
                    f.write('api.add_beam("%s","%s","%s","%s")\n'%(
                        beam.name,
                        nodes[conn[beam.name][0]].name,
                        nodes[conn[beam.name][1]].name,
                        beam.section.name)
                    )
                                    
                f.write('\n')
                f.write('api.add_loadpattern("pat1")'+'\n')
                f.write('api.add_static_case("case1")'+'\n')
                f.write('api.add_case_pattern("case1","pat1",1.0)'+'\n')
                f.write('\n')
                                        
                for load in node_loads:
                    name=load.node.name
                    f.write('api.set_nodal_load("pat1","%s",f1=%f,f2=%f,f3=%f,m1=%f,m2=%f,m3=%f)'%(
                        name,
                        load.f1*fscale,
                        load.f2*fscale,
                        load.f3*fscale,
                        load.m1*fscale**2,
                        load.m2*fscale**2,
                        load.m3*fscale**2)+'\n')
                f.write('\n')
                for res in node_restraints:
                    name=res.node.name
                    f.write('api.set_nodal_restraint("%s",%s,%s,%s,%s,%s,%s)'%(name,
                        res.restraints[0],res.restraints[1],res.restraints[2],
                        res.restraints[3],res.restraints[4],res.restraints[5],
                        )+'\n')
                f.write('\n')
                                
                f.write('api.assemble()\n')
                f.write('api.save("assembly")\n')
                        
            if py_path!=None:
                python=py_path
            else:
                python="python"
            file=os.path.join(path,"gen_assemble.py")
                            
            p = subprocess.Popen([python,file],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
            stdout,stderr = p.communicate()
            
            output='Assembled model with: \n'
            output+="%d materials"%len(model.materials)+'\n'
            output+="%d beam sections"%len(model.sections)+'\n'
            output+="%d nodes"%len(model.nodes)+'\n'
            output+="%d beams"%len(model.beams)
            
            output+='\n'
            output+='stdout : '+stdout+'\n'+'stderr : '+stderr
        
        # return outputs if you have them; here I try it for you:
        return (output, model)
