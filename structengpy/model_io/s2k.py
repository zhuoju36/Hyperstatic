# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 20:58:57 2018

@author: Dell
"""
import os

import logger
from object_model.model import Model

def import_s2k(model:Model,s2k_file):
    """
    Import geometry model from dxf file.
    
    params:
        s2k_file: str, file name with path to import.
    return:
        boolean, status of success
    """
            
    def split_row(s):
        segments = []
        flag = False
        temp = ''
        for i in s:
            if i == '"':
                flag = not flag
            if flag == True or (i != ' ' and i != '\n'):
                temp += i
            elif temp != '':
                segments.append(temp)
                temp = ''
        return segments
    
    
    def parse_lines(lines):
        data_list = []
        it = iter(lines)
        try:
            params = next(it)
            while params[-2] == '_':
                params = params[:-2] + next(it)
            params = split_row(params)
            while len(params) > 0:
                param_dict = dict(
                    [[j.strip('"') for j in i.split('=', 1)[:2]] for i in params])  # MARK: can have '=' in string
                data_list.append(param_dict)
                params = next(it)
                while params[-2] == '_':
                    params = params[:-2] + next(it)
                params = split_row(params)
        except StopIteration:
            return data_list


    try:
        f = open(s2k_file, 'r')
        f.readline()
        f.readline()
        blocks = []
        for line in f:
            if 'END TABLE DATA' in line:
                continue
            if 'TABLE:' in line:
                blocks.append([line])
                continue
            blocks[-1].append(line)
    finally:
        f.close()
    
    attrs = {}
    for block in blocks:
        attrs[block[0].split('"')[1]] = parse_lines(block[1:-1])
    
    # file=r'C:\Users\dell\Desktop\20170821_scheam2_for_zyd.s2k'
    # file = r'C:\Users\dell\Desktop\s3 -2.s2k'
    f = open(file, 'r')
    s = f.readline()
    
    jointMap = {}
    frameMap = {}
    areaMap = {}
    
    table = 'MATERIAL PROPERTIES 02 - BASIC MECHANICAL PROPERTIES'
    print ("---Read Material---")
    ETableFromMaterial = {}  # this dict and below are generated from Material table
    AlphaTableFromMaterial = {}
    if table in attrs.keys():
        block = attrs[table]
        for param_dict in block:
            mat = myModel.Material(name='mat_' + param_dict['Material'])
            E1 = eval(param_dict['E1'])
            ETableFromMaterial[param_dict['Material']] = E1
            v = 0.3
            mat.Elastic(table=[(E1, v)])
            density = eval(param_dict['UnitMass'])
            if density == 0:
                density = 1
            mat.Density(table=[(density,)])
            AlphaTableFromMaterial[param_dict['Material']] = eval(param_dict['A1'])
    
    ETable = {}  # this dict and below's keys are section name NOT material name
    AlphaTable = {}
    table = 'FRAME SECTION PROPERTIES 01 - GENERAL'
    print ("---Read Frame Properties---")
    if table in attrs.keys():
        block = attrs[table]
        for param_dict in block:
            sectionName = param_dict['SectionName']
            materialName = param_dict['Material']
            ETable[sectionName] = ETableFromMaterial[materialName]
            AlphaTable[sectionName] = AlphaTableFromMaterial[materialName]
            if param_dict['Shape'] == 'Rectangular':
                a = eval(param_dict['t3'])
                b = eval(param_dict['t2'])
                myModel.RectangularProfile(name=sectionName, a=a, b=b)
            elif param_dict['Shape'] == '"I/Wide Flange"':
                h = eval(param_dict['t3'])
                b1 = eval(param_dict['t2'])
                t1 = eval(param_dict['tf'])
                t3 = eval(param_dict['tw'])
                b2 = eval(param_dict['tf'])
                t2 = eval(param_dict['tw'])
                myModel.IProfile(name=sectionName, l=h / 2, h=h, b1=b1, b2=b2, t1=t1, t2=t2, t3=t3)
            elif param_dict['Shape'] == 'Box/Tube':
                a = eval(param_dict['t3'])
                b = eval(param_dict['t2'])
                t1 = eval(param_dict['tf'])
                t2 = eval(param_dict['tw'])
                t3 = eval(param_dict['tf'])
                t4 = eval(param_dict['tw'])
                myModel.BoxProfile(name=sectionName, uniformThickness=OFF, a=a, b=b, t1=t1, t2=t2, t3=t3, t4=t4)
            elif param_dict['Shape'] == '"SD Section"':
                area = eval(param_dict['Area'])
                i11 = eval(param_dict['I33'])
                i22 = eval(param_dict['I22'])
                i12 = 0
                j = eval(param_dict['TorsConst'])
                gammaO = 0
                gammaW = 0
                myModel.GeneralizedProfile(name=sectionName, area=area, i11=i11, i12=i12, i22=i22, j=j, gammaO=gammaO,
                                           gammaW=gammaW)
            elif param_dict['Shape'] == 'Pipe':
                r = eval(param_dict['t3']) / 2
                t = eval(param_dict['tw'])
                myModel.PipeProfile(name=sectionName, r=r, t=t)
            elif param_dict['Shape'] == 'Circle':
                r = eval(param_dict['t3']) / 2
                myModel.CircularProfile(name=sectionName, r=r)
            myModel.BeamSection(name=sectionName,
                                integration=DURING_ANALYSIS, poissonRatio=0.0, profile=sectionName,
                                material='mat_' + param_dict['Material'], temperatureVar=LINEAR, consistentMassMatrix=False)
    
    table = 'AREA SECTION PROPERTIES'
    print ("---Read Area Section Properties---")
    if table in attrs.keys():
        block = attrs[table]
        for param_dict in block:
            sectionName = param_dict['Section']
            mat = param_dict['Material']
            tck = eval(param_dict['Thickness'])
            myModel.HomogeneousShellSection(name=sectionName, material='mat_' + mat, thickness=tck, thicknessType=UNIFORM)
            # params=f.readline() #???
    
    table = 'JOINT COORDINATES'
    print ("---Read All Joints---")
    if table in attrs.keys():
        block = attrs[table]
        number = 0
        for param_dict in block:
            number += 1
            joint = eval(param_dict['Joint'])
            x = eval(param_dict['GlobalX'])
            y = eval(param_dict['GlobalY'])
            z = eval(param_dict['GlobalZ'])
            myPart.Node((x, y, z))
            jointMap[joint] = number - 1
            myPart.Set(name='Node_%d' % joint,
                       nodes=myPart.nodes[jointMap[joint]: jointMap[joint] + 1])
    
    table = 'CONNECTIVITY - FRAME'
    print ("---Now Connect Frames---")
    if table in attrs.keys():
        block = attrs[table]
        number = 0
        for param_dict in block:
            # param_dict=dict([i.split('=') for i in params])
            number += 1
            frame = eval(param_dict['Frame'])
            jointI = jointMap[eval(param_dict['JointI'])]
            jointJ = jointMap[eval(param_dict['JointJ'])]
            myPart.Element((myPart.nodes[jointI], myPart.nodes[jointJ]), LINE2)
            frameMap[frame] = number - 1
    
    frameEleNumber = len(frameMap)
    table = 'CONNECTIVITY - AREA'
    print ("---Now Connect Area---")
    if table in attrs.keys():
        block = attrs[table]
        number = 0
        for param_dict in block:
            number += 1
            area = eval(param_dict['Area'])
            numJoint = eval(param_dict['NumJoints'])
            if numJoint == 4:
                joint1 = jointMap[eval(param_dict['Joint1'])]
                joint2 = jointMap[eval(param_dict['Joint2'])]
                joint3 = jointMap[eval(param_dict['Joint3'])]
                joint4 = jointMap[eval(param_dict['Joint4'])]
                myPart.Element((myPart.nodes[joint1], myPart.nodes[joint2], myPart.nodes[joint3], myPart.nodes[joint4]),
                               QUAD4)
            if numJoint == 3:
                joint1 = jointMap[eval(param_dict['Joint1'])]
                joint2 = jointMap[eval(param_dict['Joint2'])]
                joint3 = jointMap[eval(param_dict['Joint3'])]
                myPart.Element((myPart.nodes[joint1], myPart.nodes[joint2], myPart.nodes[joint3]), TRI3)
            areaMap[
                area] = number - 1 + frameEleNumber  # MARK: should add this!!! otherwise will have the same map result with frameMap
    
    LSDict = {}  # used to store LS ==> (E, alpha) information
    table = 'FRAME SECTION ASSIGNMENTS'
    print ("---Frame Section Assignments---")
    if table in attrs.keys():
        block = attrs[table]
        sectionLabels = {}
        nodesIndexList = []
        for param_dict in block:
            frame = eval(param_dict['Frame'])
            secName = param_dict['AnalSect']
            secSet = myPart.Set(name='beam_%d' % frameMap[frame],
                                elements=myPart.elements[frameMap[frame]:frameMap[frame] + 1])
            myPart.SectionAssignment(region=secSet, sectionName=secName)
            myPart.assignBeamSectionOrientation(region=secSet, method=N1_COSINES, n1=(1, 0, 0))  # don't know quite clear
    
            if 'LS' in secName:
                # element = myPart.elements[frameMap[frame]]
                nodesIndexList.append(frameMap[frame] + 1)  # notice there should add 1
                myPart.Set(name="Element_LS_%d" % frame, elements=myPart.elements[frameMap[frame]: frameMap[frame] + 1])
                LSDict["Element_LS_%d" % frame] = (ETable[secName], AlphaTable[secName])
                # connectivity = element.connectivity
                # for index in connectivity:
                #     #myPart.Set(name = 'Node_LS_%d'%index, nodes = myPart.nodes[index : index + 1])
                #     nodesIndexList.add(index)
        # nodesIndexList = list(nodesIndexList)
        # myPart.Set(name = 'Node_LS', nodes = myPart.nodes.sequenceFromLabels(nodesIndexList))
        myPart.Set(name='Elements_LS', elements=myPart.elements.sequenceFromLabels(nodesIndexList))
    
    table = 'AREA SECTION ASSIGNMENTS'
    print ("---Area Section Assignments---")
    if table in attrs.keys():
        block = attrs[table]
        sectionSets = {}
        for param_dict in block:
            area = eval(param_dict['Area'])
            secName = param_dict['Section']
            secSet = myPart.Set(name='face_%d' % areaMap[area], elements=myPart.elements[areaMap[area]:areaMap[
                                                                                                           area] + 1])  # ??? .elements(areaMap[area]) TEST RESULT: should be a sequence, so use this representation!!!
            # secSet=myPart.Set(name='face_%d'%areaMap[area],elements=myPart.elements[areaMap[area])
            myPart.SectionAssignment(region=secSet, sectionName=secName)
    
    
    def sort_load_case(block):
        def split(block, plc_list):
            block_a = []
            block_b = []
            for param_dict in block:
                if param_dict['Type'] != 'NonStatic' or param_dict['InitialCond'] in plc_list:
                    block_a.append(param_dict)
                else:
                    block_b.append(param_dict)
            return block_a, block_b
    
        block_a, block_b = split(block, ['Zero'])
        plc_list = [i['Case'] for i in block_a]
        while len(block_a) < len(block):
            a, block_b = split(block_b, plc_list)
            block_a += a
            plc_list = [i['Case'] for i in block_a]
        return block_a
    
    
    import assembly
    
    myAssembly = myModel.rootAssembly
    myInstance = myAssembly.Instance(name='all', part=myPart, dependent=OFF)
    
    
    def assign_area_load(loadcase):
        table = 'CASE - STATIC 1 - LOAD ASSIGNMENTS'
        block = [i for i in attrs[table] if i['Case'] == loadcase]
        for param_dict in block:
            loadName = param_dict['LoadName']
            loadSF = eval(param_dict['LoadName'])
            assign_area_uniform(loadcase, loadName, loadSF)
    
    
    def assign_area_uniform(loadpattern, loadSF):
        table = 'AREA LOADS - UNIFORM'
        block = [i for i in attrs[table] if i['LoadPat'] == loadpattern]
        for param_dict in block:
            area = eval(param_dict['Area'])
            magn = eval(param_dict['UnifLoad']) * loadSF
            direction = param_dict['Dir']
            if direction == 'Gravity':
                directionVector = [(0, 0, 0), (0, 0, -1)]
                print('ho')
            myModel.SurfaceTraction(
                name=loadpattern,
                createStepName='case_Zero',
                region=myPart.Set(
                    name='face_%d' % areaMap[area],
                    elements=myPart.elements[areaMap[area]:areaMap[area] + 1]
                ),
                magnitude=magn,
                directionVector=directionVector,
                traction=GENERAL,
            )
    
    
    table = 'JOINT RESTRAINT ASSIGNMENTS'
    if table in attrs.keys():
        block = attrs[table]
        for param_dict in block:
            joint = eval(param_dict['Joint'])
            u1 = SET if param_dict['U1'] == 'Yes' else UNSET
            u2 = SET if param_dict['U2'] == 'Yes' else UNSET
            u3 = SET if param_dict['U3'] == 'Yes' else UNSET
            r1 = SET if param_dict['R1'] == 'Yes' else UNSET
            r2 = SET if param_dict['R2'] == 'Yes' else UNSET
            r3 = SET if param_dict['R3'] == 'Yes' else UNSET
            myModel.DisplacementBC(
                name='BC_J%d' % jointMap[joint],
                createStepName='Initial',
                region=myAssembly.Set(
                    name='set_J%d' % jointMap[joint],
                    nodes=myInstance.nodes[jointMap[joint]:jointMap[joint] + 1]
                    # the same question, for the case the the node is not in the nodes???
                ),
                u1=u1, u2=u2, u3=u3, ur1=r1, ur2=r2, ur3=r3
            )
    
    
            # scan the LOAD CASE DIFINITION:
            # a load case struct is like this:
            # {name: 'S+D+L', loadPattern: ('D', 'L'), scale:(1.0, 1.0), catagory: 'nonlinear',
            # former: 'S+PRES', stepName: 'Step-S+D+L', caseName: 'Case-S+PRES'}
    table = 'LOAD CASE DEFINITIONS'
    print ("---Start Generate Load Case Tree---")
    loadCaseDict = {}
    if table in attrs.keys():
        block = attrs[table]
        for param_dict in block:
            if param_dict['Type'] == 'LinRespSpec':
                continue
            loadCase = {}
            loadCase['name'] = param_dict['Case']
            loadCase['catagory'] = param_dict['Type']
            loadCase['former'] = param_dict['InitialCond']
            loadCase['load pattern'] = []
            loadCase['scale'] = {}
            loadCase['case name'] = 'case-' + param_dict['Case'].replace('.', '')
            loadCase['step name'] = 'step-' + param_dict['Case'].replace('.', '')
            # loadCaseList.append(loadCase)
            loadCaseDict[loadCase[
                'name']] = loadCase  # this is only useful in the next step, we will at last only use this dictionary's values
    
    # now scan the CASE - STATIC 1 - LOAD ASSIGNMENTS:
    table = 'CASE - STATIC 1 - LOAD ASSIGNMENTS'
    if table in attrs.keys():
        block = attrs[table]
        for param_dict in block:
            loadCase = loadCaseDict[param_dict['Case']]  # find the load case
            loadCase['load pattern'].append(param_dict['LoadName'])  # add the load pattern
            loadCase['scale'][param_dict['LoadName']] = param_dict['LoadSF']  # add the load pattern's scale
    
    
    # define a recursion function to calculate every load case's depth in order to sort them latter
    def giveDepth(loadCaseDict):
        cache = {}
    
        def recursionSort(loadCase):
            if loadCase['name'] in cache.keys():
                return cache[loadCase['name']]
            if loadCase['former'] == 'Zero':
                cache[loadCase['name']] = 1
                return 1
            else:
                result = 1 + recursionSort(loadCaseDict[loadCase['former']])
                cache[loadCase['name']] = result
                return result
    
        # now give the depth attribute:
        for loadCase in loadCaseDict.values():
            loadCase['depth'] = recursionSort(loadCase)
    
    
    # call giveDepth:
    
    giveDepth(loadCaseDict)
    
    # sort all the load cases according to the depth
    chosenCaseKey = [""]  # use a list so that the clickMe() function can change its value
    import sys
    # sys.path.append('C:\\Program Files\\Python36\\lib\\tkinter')
    import Tkinter as tk
    # from Tkinter import ttk
    import ttk
    
    win = tk.Tk()
    win.title("Choose the Case you want to analyse")
    
    ttk.Label(win, text="Analyse Case:").grid(column=0, row=0)
    
    
    def clickMe():
        chosenCaseKey[0] = caseChosen.get()
        if chosenCaseKey[0] != "":
            win.destroy()
    
    
    action = ttk.Button(win, text="OK", command=clickMe)
    action.grid(column=1, row=1)
    
    case = tk.StringVar()
    caseChosen = ttk.Combobox(win, width=20, textvariable=case)
    caseChosen['values'] = tuple(loadCaseDict.keys())
    caseChosen.grid(column=0, row=1)
    
    print ("-----Choose a case you want to analyse-")
    win.mainloop()
    
    loadCaseList = sorted(loadCaseDict.values(), key=lambda loadCase: loadCase['depth'])
    # print(loadCaseList)
    
    # choose the case you want to analyse:
    # chooseCase = loadCaseDict['A-S+D+L+0.6T']
    print ("Your chosen case is: " + chosenCaseKey[0])
    chooseCase = loadCaseDict[chosenCaseKey[0]]
    chooseCaseChain = []
    # nlgeom = ON if chooseCase['catagory'] == 'NonStatic' else OFF
    # myModel.StaticStep(name = chooseCase['step name'], previous = 'Initial', nlgeom = nlgeom)
    while chooseCase['depth'] != 1:
        # print(chooseCase)
        nlgeom = ON if chooseCase['catagory'] == 'NonStatic' else OFF
        myModel.StaticStep(name=chooseCase['step name'], previous='Initial', nlgeom=nlgeom)
        chooseCaseChain.append(chooseCase)
        chooseCase = loadCaseDict[chooseCase['former']]
        # print(chooseCase)
    nlgeom = ON if chooseCase['catagory'] == 'NonStatic' else OFF
    myModel.StaticStep(name=chooseCase['step name'], previous='Initial', nlgeom=nlgeom)
    chooseCaseChain.append(chooseCase)
    
    
    # add load to every step help function
    def addAreaLoad(loadCase):
        loadPatList = loadCase['load pattern']
        print(loadPatList)
        table = 'AREA LOADS - UNIFORM'
        if table in attrs.keys():
            block = attrs[table]
            # add face load
            for param_dict in block:
                loadPat = param_dict['LoadPat']
                print(loadPat)
                if loadPat in loadPatList:
                    area = eval(param_dict['Area'])
                    name = loadPat + '_' + loadCase['step name'] + '_%d' % areaMap[area]
                    createStepName = loadCase['step name']
                    side1Elements1 = myInstance.elements[areaMap[area]: areaMap[area] + 1]  # SHOULDN'T use this!!!
                    region = myAssembly.Surface(side1Elements=side1Elements1,
                                                name='suf_' + loadCase['step name'] + '_' + loadPat + '_%d' % areaMap[area]
                                                )
                    magn = eval(param_dict['UnifLoad'])
                    print("loadPat:" + loadPat)
                    print(magn)
                    if param_dict['Dir'] == 'Gravity':
                        directionVector = ((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
                    distributionType = UNIFORM
                    traction = GENERAL
                    myModel.SurfaceTraction(
                        name=name,
                        createStepName=createStepName,
                        region=region,
                        magnitude=magn,
                        directionVector=directionVector,
                        distributionType=distributionType,
                        traction=traction
                    )
    
        # uniform to frame:
        def uniformToFrame(param_dict, scale):
            area = eval(param_dict['Area'])
            magn = eval(param_dict['UnifLoad'])
            element = myInstance.elements[
                areaMap[area]]  # SHOULDN'T use this! because frame element and area element have the same
            table = 'CONNECTIVITY - AREA'
            if table in attrs.keys():
                block = attrs[table]
                for param_dict2 in block:
                    if area == eval(param_dict2['Area']):
                        break
                areaArea = eval(param_dict2['AreaArea'])
                numJoints = eval(param_dict2['NumJoints'])
                magnEveryJoint = scale * magn * areaArea / numJoints
                for i in range(0, numJoints):
                    node = eval(param_dict2['Joint%d' % (i + 1)])
                    node = jointMap[node]
                    # print("node: %d"%node)
                    # print(magnEveryJoint)
                    myModel.ConcentratedForce(name=loadPat + '_Con_%d' % node + '_from_%d' % area,
                                              createStepName=loadCase['step name'],
                                              region=myAssembly.Set(name='Set_ConNode_%d' % node,
                                                                    nodes=myInstance.nodes[node: node + 1]),
                                              cf1=0,
                                              cf2=0,
                                              cf3=-1 * magnEveryJoint
                                              )
    
            def addToJoint(magn, area):  # brute force!!! can consider use a structure before
                table = 'CONNECTIVITY - AREA'
                if table in attrs.keys():
                    block = attrs[table]
                    for param_dict in block:
                        if area == eval(param_dict['Area']):
                            break
                    areaArea = eval(param_dict['AreaArea'])
                    numJoints = eval(param_dict['NumJoints'])
                    magnEveryJoint = magn * areaArea / numJoints
                    for i in range(0, numJoints):
                        node = eval(param_dict['Joint%d' % (i + 1)])
                        node = jointMap[node]
                        # jointForceDict[node] += magnEveryJoint
    
                        # addToJoint(magn, area)
                        # print(jointForceDict)
    
        table = 'AREA LOADS - UNIFORM TO FRAME'
        if table in attrs.keys():
            block = attrs[table]
            jointForceDict = collections.defaultdict(float)
            for param_dict in block:
                loadPat = param_dict['LoadPat']
                if loadPat in loadPatList:
                    # print(loadPat)
                    scale = eval(loadCase['scale'][loadPat])
                    uniformToFrame(param_dict, scale)
                    for nodeIndex, magnEveryJoint in jointForceDict.items():
                        scale = eval(loadCase['scale'][loadPat])
                        myModel.ConcentratedForce(name=loadPat + '_Con_%d' % nodeIndex,
                                                  createStepName=loadCase['step name'],
                                                  region=myAssembly.Set(name='Set_ConNode_%d' % nodeIndex,
                                                                        nodes=myInstance.nodes[nodeIndex: nodeIndex + 1]),
                                                  cf1=0,
                                                  cf2=0,
                                                  cf3=-1 * magnEveryJoint * scale
                                                  )
    
    
                        # addToJoint(magn, nodeList)
    
    
    
    
                        #        def addToJoint(magn, nodeList):
                        #            number = len(nodeList)
                        #            for node in nodeList:
                        #
                        #                jointForcDict[] +=
    
                        # add S
        if 'S' in loadCase['load pattern']:
            for element in myInstance.elements:
                region = myAssembly.Set(name='Set_S_%d' % element.label,
                                        elements=myInstance.elements[element.label - 1: element.label])
                myModel.Gravity(
                    name='S_%d' % element.label,
                    createStepName=loadCase['step name'],
                    region=region,
                    comp1=0,
                    comp2=0,
                    comp3=-9800  # notice this is only used when unit is N/mm
                )
    
    
    # add load to area
    print ("Add Area Load")
    chooseCaseChain = chooseCaseChain[::-1]
    for loadCase in chooseCaseChain:
        addAreaLoad(loadCase)
    
    # ready write input file
    mdb.Job(name='Job-structure', model='Model-1', description='', type=ANALYSIS,
            atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90,
            memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
            explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF,
            modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='',
            scratch='', resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=1,
            numGPUs=0)
    mdb.jobs['Job-structure'].writeInput(consistencyChecking=OFF)
    
    # ready open the input file created before
    dlg = win32ui.CreateFileDialog(1)
    dlg.SetOFNInitialDir('D:')
    dlg.DoModal()
    fileDir = dlg.GetPathName()
    print (fileDir)
    tmpDir = r'D:\temp'
    # fileDir = tmpDir + r'\Job-structure.inp'
    inputFile = open(fileDir, 'r')
    
    # find **STEP position, and insert contents there
    # this method should read the input file into memory
    lines = []
    insertPosition = 0
    found = False
    lineNumber = 0
    for line in inputFile:
        lines.append(line)
        if (not found) and ('** STEP:' in line):
            insertPosition = lineNumber
            found = True
        lineNumber += 1
    inputFile.close()
    
    addContent = ""
    table = 'FRAME LOADS - TEMPERATURE'
    if table in attrs.keys():
        addContent += "*INITIAL CONDITIONS, TYPE = STRESS\n"
        block = attrs[table]
        for param_dict in block:
            frame = eval(param_dict['Frame'])
            temperature = abs(eval(param_dict['Temp']))  # use abs value
            name = "Element_LS_%d" % frame
            number = LSDict[name][0] * LSDict[name][1] * temperature  # stress = E*alpha*delta_T
            addContent += "all.%s, %f\n" % (name, number)
    
    # addContent = '*INITIAL CONDITIONS, TYPE = STRESS\nall.Elements_LS, 241.02\n'
    lines.insert(insertPosition, addContent)
    s = ''.join(lines)
    fp = open(fileDir, 'w')
    fp.write(s)
    fp.close()
    
    # ready import the input file as model
    mdb.ModelFromInputFile(name='Job-structure', inputFileName=fileDir)