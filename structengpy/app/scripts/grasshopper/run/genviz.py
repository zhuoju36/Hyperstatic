from ghpythonlib.componentbase import executingcomponent as component
import Grasshopper, GhPython
import System
import Rhino
import rhinoscriptsyntax as rs
import os
import subprocess


class MyComponent(component):
    
    def RunScript(self, model, open_dir, run):
        """Generate visualization scripts.
            Inputs:
                model: assembled model.
                open_dir: (bool) open directory or not after running.
                run: (bool) run this component.
            Output:
                output: success or not"""
                                
        __author__ = "Zhuoju Huang"
        __version__ = "2022.07.12"
                                
        output="Not yet run."
        path=model.path
        python=model.py_path
            
        if run==True:
            ## result viewer
            file=os.path.join(path,"model_viz.py")
            with open(file, "w+") as f:
                f.write("""
from structengpy.app.viz.viz_core.viz_core_model import Viewer\n
path=r"%s"
viewer=Viewer(path,"assembly")
viewer.run()
"""%path)
                        
            file=os.path.join(path,"model_viz.bat")
            with open(file, "w+") as f:
                f.write("%s %s"%(python,os.path.join(os.curdir,"model_viz.py")))

            ## result viewer
            file=os.path.join(path,"result_viz.py")
            with open(file, "w+") as f:
                f.write("""
from structengpy.app.viz.viz_core.viz_core_result_deformation import Viewer\n
path=r"%s"
viewer=Viewer(path,"assembly")
viewer.run()
"""%path)
                        
            file=os.path.join(path,"result_viz.bat")
            with open(file, "w+") as f:
                f.write("%s %s"%(python,os.path.join(os.curdir,"result_viz.py")))
        output="success"
        if open_dir:
            subprocess.Popen(['explorer.exe',path],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        # return outputs if you have them; here I try it for you:
        return output
