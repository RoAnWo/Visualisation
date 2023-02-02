# Import javascript modules
from js import THREE, window, document, Object, console

# Import pyscript / pyodide modules
from pyodide.ffi import create_proxy, to_js

#Import python module
import math
#import shapely

# Import NumPy as np
import numpy as np
from random import choices,choice, randint
import random
from time import time
from shapely import geometry
from collections import OrderedDict


#-----------------------------------------------------------------------
# USE THIS FUNCTION TO WRITE THE MAIN PROGRAM

  
   

def main():
    # VISUAL SETUP
    # Declare the variables

    global renderer, scene, camera, controls,composer, light2, light

    #Set up the renderer

    renderer = THREE.WebGLRenderer.new()
    renderer.setPixelRatio( window.devicePixelRatio )
    renderer.setSize(window.innerWidth, window.innerHeight)
    document.body.appendChild(renderer.domElement)

 # Set up the scene

    scene = THREE.Scene.new()
    back_color = THREE.Color.new(200,200,200)
    scene.background = back_color
    camera = THREE.PerspectiveCamera.new(30, window.innerWidth/window.innerHeight,0.1, 10000)
    camera.position.y = -1000
    camera.position.x = 100
    camera.position.z = 200
    camera.up = THREE.Vector3.new( 0, 0, 1 )
    scene.add(camera)

    light2 = THREE.AmbientLight.new()
    light = THREE.PointLight.new(THREE.Color.new(255,255,233), 0.001,10000,20)
    light.position.set(-50, -50, 200)
    
    light.castShadow = True
    light.shadow.mapSize.width = 512
    light.shadow.mapSize.height = 512
    light.shadow.camera.near = 5
    light.shadow.camera.far = 500
    renderer.shadowMap.enabled = True
    renderer.shadowMap.type = THREE.PCFSoftShadowMap
    
    scene.add(light, light2)
    # axesHelper
    # axesHelper = THREE.AxesHelper.new(100)
    # scene.add(axesHelper)
    
    # Graphic Post Processing
    global composer
    post_process()

    # Set up responsive window

    resize_proxy = create_proxy(on_window_resize)
    window.addEventListener('resize', resize_proxy) 

    controls = THREE.OrbitControls.new(camera, renderer.domElement)
    global input_param   

    input_param = {  
    "population" : 500,
    "iputOld" : 500,
    "population_density" : 4,
    "populationold_density" : 4,
    
    #Industrial storagespace
    "heightperfloorI"   : 5,
    "oldheightperfloorI" : 5,
    "distancestreetI" : 5, 
    "OlddistancestreetI" : 5,
    
    #0ffice
    "heightperfloorO"   : 4,
    "oldheightperfloorO" : 4,
    "distancetostreetO"   : 3,
    "olddistancetostreetO" : 3,
    
    "LivingIndustrial" : 55,
    
    "floors" : 1, 
    "offsetR": 4, 
    "offsetB" : 3, 
    "offsetH" : 2, 
    "heightperfloorR": 4, 
    "heightperfloorB": 3.5, 
    "heightperfloorH": 4, 
    
    
    "MainStreets" : False, 
    "SecondaryStreets":False,
    "AssignUsage" :False,
    "GenerateCity" : False,
    "Generate" : Generate,
    "RegenerateAll" : regenerateAll
   
    }
    input_param = Object.fromEntries(to_js(input_param))
    #-----------------------------------------------------------------------
     #GUI
    global gui
    gui = window.lil.GUI.new()
    
    
    gen_folder = gui.addFolder('generate step-by-step')
    gen_folder.add(input_param, 'MainStreets')
    gen_folder.add(input_param, 'SecondaryStreets')
    gen_folder.add(input_param, 'AssignUsage')
    gen_folder.add(input_param, 'LivingIndustrial', 10,100,1)
    
    gen_folder.add(input_param, 'GenerateCity')
    
    gen_folder.add(input_param, 'Generate')
    gen_folder.add(input_param, 'RegenerateAll')
    
    
    
    param_folder = gui.addFolder('values')
    param_folder.add(input_param, 'population', 0,10000,1)
    param_folder.add(input_param, 'population_density', 0,10,1)

    
    I_folder = gui.addFolder('Industrial Storage')
    I_folder.add(input_param, 'heightperfloorI', 0,8,1)
    I_folder.add(input_param, 'distancestreetI', 0,8,1)

    I_folder.open()
     
    I_folder = gui.addFolder('Offices')
    I_folder.add(input_param, 'heightperfloorO', 0,5,0.2)
    # I_folder.add(input_param, 'distancetostreetO', 2,8,1)
    I_folder.open()

    gen_folder.open()
    global linesIfinal, meshesIfinal

    global count
    count = 0
    
    

    #-----------------------------------------------------------------------

    # RENDER + UPDATE THE SCENE AND GEOMETRIES
    #Space for potential GUI- might be added later (still WIP)!
    
    render()



def Generate():
    
    global light2, light, count
    scene.clear()
    scene.add(light2, light)
 
    if count < 1 or input_param.AssignUsage == True:
        generatePlotsAndAssign()
        count += 1
    
    if input_param.GenerateCity == True:
        global meshesfinal_listL, linesfinal_listL
        generateL ()
        global meshfinal_list2, linefinal_list2, meshplaneI
        generateI()
        global meshO_list2, lineO_list2
        generateO()
        generateG()
        generateE()
        
    

def generatePlotsAndAssign():
    global INPUT_LINES, PLOTS, toplots, NEIGHBOURS
    INPUT_LINES = [[(int(point[0]), int(point[1])) for point in line] for line in lines]
    ##########################################################################################
    PLOTS= loop_finder(INPUT_LINES)
    #print("Plots:",PLOTS)
    ##########################################################################################
    toplots = [[tuple(x) for x in sublist] for sublist in PLOTS]#Convert in Tuples
    NEIGHBOURS = find_overlapping_plots(toplots)
    #print("Neighbours:",NEIGHBOURS)
    ##########################################################################################
    global DICTIONARY, POSSIBLE_CHANGES
    DICTIONARY = convert_data(NEIGHBOURS)
    DISTRIBUTION=find_solution(DICTIONARY)
    POSSIBLE_CHANGES=random_distribution(DICTIONARY)
    
    colorPlots()
    print ("Distribution",DISTRIBUTION)

def regenerateAll():
    global light2, light
    scene.clear()
    scene.add(light2, light)
    
    generatePlotsAndAssign()
    global meshesfinal_listL, linesfinal_listL
    generateL ()
    global meshfinal_list2, linefinal_list2, meshplaneI
    generateI()
    global meshO_list2, lineO_list2
    generateO()
    generateG() 
    generateE()
    
    
    # global PLOTS, DICTIONARY
    # PlotsNumpy = generateNumpyArray (PLOTS)
    # for i in DICTIONARY.keys():
    #     if DICTIONARY[i]['value'] == "L":
    #         Boundary = PlotsNumpy[i]
    #         print("Boundary", Boundary)
    
    #         print(polygonDivider(Boundary,200, 25000, 1, True,Boundary))
    
    
    # planeGeometry = THREE.PlaneGeometry.new( 2000, 2000, 32, 32 )
    
    # planeMaterial = THREE.MeshPhongMaterial.new()
    
    # plane = THREE.Mesh.new( planeGeometry, planeMaterial )
    
    # plane.translateZ(-2)
    # # plane.transparent = True 
    # # plane.opacity = 0.5
    # plane.receiveShadow = True
   
    
    # scene.add(plane)      
    
    planeGeometry = THREE.PlaneGeometry.new( 2000, 2000, 32, 32 )
    color = THREE.Color.new("rgb(200,200,200)")
    planeMaterial = THREE.ShadowMaterial.new()
    planeMaterial.color = color
    
    plane = THREE.Mesh.new( planeGeometry, planeMaterial )
    
    plane.translateZ(-2)
    plane.transparent = True 
    plane.opacity = 0
    plane.receiveShadow = True
    
    scene.add(plane) 
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#CLASS AND GENERATE MAIN DICTIONARY
global plotInformation

class plotInformation:
    def __init__(self, name, outerboundary, plotarea, neighbour, possibleChanges, floors, areatype):
        self.name = name
        self.outerboundary = outerboundary
        self.newouterboundary = 0
        self.offsetvalue = 0
        self.plotarea = plotarea
        self.neighbour = neighbour
        self.possibleChanges = possibleChanges
        self.floors = floors
        self.areatype = areatype
        self.currentArea = 0
    
    def get_area(self):
        return self.plotarea
    
    def get_outerboundary(self):
        return self.outerboundary
    
    def set_floors(self, floors):
        self.floors = floors
    
    def reset(self):
        self.currentArea = 0
    
    def get_floors(self):
        return self.floors
    
    def returncurrent(self):
        return self.currentArea
    
    def get_area_type(self):
        return self.areatype
        
    def get_currentarea_oftype(self, typus):
        self.areatype = typus 
        
        if typus == 1:
            self.currentArea,  self.newouterboundary, self.offsetvalue  = calc_R(self.outerboundary)
            self.currentArea =  self.plotarea
        elif typus == 2: 
            self.currentArea,  self.newouterboundary, self.offsetvalue  = calc_R(self.outerboundary)
            self.currentArea = self.plotarea *2
        elif typus == 3: 
            self.currentArea,  self.newouterboundary, self.offsetvalue  = calc_B(self.outerboundary)
            self.currentArea = self.currentArea *3
        elif typus == 4: 
            self.currentArea,  self.newouterboundary, self.offsetvalue = calc_B(self.outerboundary)
            self.currentArea = self.currentArea *4
        elif typus == 5: 
            self.currentArea,  self.newouterboundary, self.offsetvalue  =  calc_B(self.outerboundary)
            self.currentArea = self.currentArea *5 
        elif typus == 6: 
            self.currentArea,  self.newouterboundary, self.offsetvalue  = calc_B(self.outerboundary)
            self.currentArea = self.currentArea *6
        elif typus == 7: 
            self.currentArea,  self.newouterboundary, self.offsetvalue  = calc_H(self.outerboundary)
            self.currentArea = self.plotarea *7
        elif typus == 8: 
            self.currentArea,  self.newouterboundary, self.offsetvalue  = calc_H(self.outerboundary)
            self.currentArea = self.plotarea *8
        elif typus == 9: 
            self.currentArea,  self.newouterboundary, self.offsetvalue  = calc_H(self.outerboundary)
            self.currentArea = self.plotarea *9
        elif typus == 10: 
            self.currentArea,  self.newouterboundary, self.offsetvalue  = calc_H(self.outerboundary)
            self.currentArea = self.plotarea *10

    
        return self.currentArea

def sortedDictPlotAreas (Dict_R, Plotsnumpyn, DictPossibleChanges):
    
    plotinfo = {} 
    for i in Dict_R.keys():
        if Dict_R[i]['value'] == "L":
            
            Boundary = Plotsnumpyn[i]
            #print(Boundary)
            #return offsetet area of each plot and original boundaries 
            
            calc_area = calc_plotArea(Boundary)
            # print("check_area", calc_area)
            # total area all plots with this value 

            #generate new dictionary with all the informations with the right value 
            plot = plotInformation(i, Boundary, calc_area, Dict_R[i]['neighbours'], DictPossibleChanges[1][i], 0, 0)
            plotinfo[i] = {'Plotobject': plot}
    

    #sort dictionary 
    dict_sort = {}
    dict_sort = sort_dict(plotinfo)
    
    return dict_sort

def colorPlots():
    global PLOTS
    PlotsNumpy = generateNumpyArray (PLOTS)
    for i in DICTIONARY.keys():
        if DICTIONARY[i]['value'] == "I":
            
            Boundary = PlotsNumpy[i]
            G(Boundary, THREE.Color.new("rgb(150,150,150)") )
    

        if DICTIONARY[i]['value'] == "E":
            
            Boundary = PlotsNumpy[i]
            G(Boundary, THREE.Color.new("rgb(214,182,148)") )
        
        if DICTIONARY[i]['value'] == "L":
            
            Boundary = PlotsNumpy[i]
            G(Boundary, THREE.Color.new("rgb(174,155,148)") )
        
        if DICTIONARY[i]['value'] == "O":
            
            Boundary = PlotsNumpy[i]
            G(Boundary, THREE.Color.new("rgb(161,167,174)") )
        
        if DICTIONARY[i]['value'] == "G":
            
            Boundary = PlotsNumpy[i]
            G(Boundary, THREE.Color.new("rgb(194,204,185)") )
    
global scene 
def generateL ():
    global PlotsNumpy, dict_sorted, DICTIONARY, PLOTS
    PlotsNumpy = generateNumpyArray (PLOTS)
    dict_sorted = sortedDictPlotAreas (DICTIONARY, PlotsNumpy, POSSIBLE_CHANGES )
    
    global meshesfinal_listL, linesfinal_listL, groundsfinal, greenPG
    meshesfinal_listL, linesfinal_listL, groundsfinal, greenPG = generateTypeL(dict_sorted, input_param.offsetR, input_param.offsetH, input_param.heightperfloorR, input_param.heightperfloorB, input_param.heightperfloorH, input_param.population, input_param.population_density)

def generateI():
    
    global meshfinal_list2, linefinal_list2, meshplaneI
    meshfinal_list2 = []
    linefinal_list2 = []
    meshplaneI = []
    
    for i in DICTIONARY.keys():
        if DICTIONARY[i]['value'] == "I":
            #loop_check_angle(PLOTS)
        
            Boundary = PlotsNumpy[i]

        
            linesI, meshesI, planeI = offsetAndGenerateShapeI(Boundary,input_param.distancestreetI, THREE.Color.new("rgb(180,180,180)"), THREE.Color.new("rgb(150,150,150)"),  THREE.Color.new("rgb(150,150,150)"),1, input_param.heightperfloorI)
            
            linefinal_list2.append(linesI)
            meshfinal_list2.append(meshesI)
            meshplaneI.append(planeI)

def generateO():
    
    global meshO_list2, lineO_list2, meshplaneO
    meshO_list2 = []
    lineO_list2 = []
    meshplaneO = []
    
    for i in DICTIONARY.keys():
        if DICTIONARY[i]['value'] == "O":
            #loop_check_angle(PLOTS)
        
            Boundary = PlotsNumpy[i]
            
            floors = randint(8,15)
            
            linesO, meshesO, planeO = offsetAndGenerateShapeO(Boundary,THREE.Color.new("rgb(200,205,210)"), THREE.Color.new("rgb(161,167,174)"),  THREE.Color.new("rgb(161,167,174)"),floors, input_param.heightperfloorO)
            
            lineO_list2.append(linesO)
            meshO_list2.append(meshesO)
            meshplaneO.append(planeO)

def generateG():
    for i in DICTIONARY.keys():
        if DICTIONARY[i]['value'] == "G":
            
            Boundary = PlotsNumpy[i]
            
            G(Boundary, THREE.Color.new("rgb(194,204,185)") )

def generateE():
    for i in DICTIONARY.keys():
        if DICTIONARY[i]['value'] == "E":
 
            Boundary = PlotsNumpy[i]
            E(Boundary, THREE.Color.new("rgb(226,207,186)"), THREE.Color.new("rgb(240,225,210)"),  THREE.Color.new("rgb(226,207,186)"), 1, 4)
  

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#UPDATE FUNCTIONS 

def updateI():
    
    global meshfinal_list2, linefinal_list2, meshplaneI, DICTIONARY, PlotsNumpy, scene
  
   
    if input_param.oldheightperfloorI != input_param.heightperfloorI or input_param.distancestreetI != input_param.OlddistancestreetI:
     
        for sub_list in linefinal_list2:
            for line in sub_list:
                scene.remove(line)    
        
        for sublist2 in meshfinal_list2:
            for mesh in sublist2:
                scene.remove(mesh)
        
        for mesh in meshplaneI:
            scene.remove(mesh)
    
     
        linefinal_list2 = []
        meshfinal_list2 = []
        meshplaneI = []

        
        generateI()
   
            
    input_param.oldheightperfloorI = input_param.heightperfloorI
    input_param.OlddistancestreetI = input_param.distancestreetI 

def updateO():
    global meshO_list2, lineO_list2, meshplaneO, DICTIONARY, PlotsNumpy, scene
    if input_param.oldheightperfloorO != input_param.heightperfloorO:
        # input_param.distancetostreetO != input_param.olddistancetostreetO
        
        for sub_list in lineO_list2:
            for line in sub_list:
                scene.remove(line)    
        
        for sublist2 in meshO_list2:
            for mesh in sublist2:
                scene.remove(mesh)
        
        for mesh in meshplaneO:
            scene.remove(mesh)
    
     
        meshO_list2 = []
        lineO_list2 = []
        meshplaneO = []
        
        
        generateO()
            
    input_param.oldheightperfloorO = input_param.heightperfloorO

def updateL ():
  
    global meshesfinal_listL, linesfinal_listL, greenPG,  groundsfinal, DICTIONARY, PlotsNumpy, POSSIBLE_CHANGES, scene
    if input_param.populationold_density != input_param.population_density or input_param.iputOld != input_param.population:
      
        for sub_list in linesfinal_listL:
            for line in sub_list:
                scene.remove(line)    
        
        for sublist2 in meshesfinal_listL:
            for mesh in sublist2:
                scene.remove(mesh)
        print("groundsfinal", groundsfinal)
        for i in range(len(groundsfinal)):
            scene.remove(groundsfinal[i])
        
        for mesh in greenPG:
            scene.remove(mesh)
            
        
     
        meshesfinal_listL = []
        linesfinal_listL = []
        groundsfinal = []
        greenPG = []
        
        
        generateL ()
            
    input_param.iputOld = input_param.population
    input_param.populationold_density = input_param.population_density

# CALCULATE FUNCTIONS
def Area(corners):

    n = len(corners) # of corners
    area = 0

    for i in range(n):
        j = (i + 1) % n
        area += (corners[i][0] * corners[j][1])
        area -= (corners[j][0] * corners[i][1])
    area = abs(area)//2.0

    return area

def calc_plotArea(arraypoints):
    
    areaOuterBoundary = Area(arraypoints)
    return areaOuterBoundary

def calculatetype (dict_sorted, density ,population, maxType):
    
    choose_type = density
    
    
    area_all = 0 
    while choose_type < maxType:
        for i in dict_sorted.keys():
            currentArea = 0

            if dict_sorted[i]['Plotobject'].get_area_type() != 0:
                currentArea = dict_sorted[i]['Plotobject'].returncurrent()
            
            builtarea_per_plot = dict_sorted[i]['Plotobject'].get_currentarea_oftype(choose_type)
            #print ("churrentareaplot", builtarea_per_plot)
            area_all = area_all - currentArea
            area_all = area_all + builtarea_per_plot
            population_possible = area_all//30
            #print("i",i, "area_all",area_all,"current_Area",currentArea, "population_possible", population_possible)
            
            if population_possible >= population:
                #print("choose_type return 1", choose_type)
                return 
        
        choose_type += 1
        #print("choose_type return 2", choose_type)   
    return             

def calc_B (arraypoints):

    Xcoordinatesb, Ycoordinatesb = generatexy (arraypoints)
    Xcoordinates, Ycoordinates = makeOffsetPoly(Xcoordinatesb,Ycoordinatesb, 5)

    OffsetX, OffsetY = makeOffsetPoly(Xcoordinates,Ycoordinates, 2)
    newOuterboundary = convert_result_check_W(OffsetX, OffsetY)
    
    # print (("1:", OffsetX))
    # convertOuterBoundary = convert_result_check_W(OffsetX, OffsetY)
    areaOuterBoundary = Area(newOuterboundary)
   
    boundarylengths = lengthBoundary(OffsetX, OffsetY)
    # print ("boundarylengths", boundarylengths)
    #print("oldbound", min(boundarylengths))
    
    
    offsetvalue = 3
    while min(boundarylengths) > 15:
        
        Oldoffset = offsetvalue
        #print("Oldoffset", Oldoffset)

        offsetvalue += 1
        
        Offset2X, Offset2Y = makeOffsetPoly(OffsetX, OffsetY, offsetvalue)
        boundarylengths = lengthBoundary(Offset2X, Offset2Y)
        #print("boundarylengths", min(boundarylengths))
        #print (Offset2X)
        Points_2_check = convert_into_Points(Offset2X, Offset2Y)
    
        if min(Offset2X) == min(OffsetX) or determine_loop_direction(Points_2_check) == "Counterclockwise":
           
            
            Offset2X, Offset2Y = makeOffsetPoly(OffsetX, OffsetY, Oldoffset)
            convertInnerBoundary = convert_result_check_W(Offset2X, Offset2Y)
            areaInnerBoundary = Area(convertInnerBoundary)
            final_area = areaOuterBoundary - areaInnerBoundary
            
            return (final_area, newOuterboundary,Oldoffset)

        else: 
            convertInnerBoundary = convert_result_check_W(Offset2X, Offset2Y)
            areaInnerBoundary = Area(convertInnerBoundary)
            final_area = areaOuterBoundary - areaInnerBoundary

    return (final_area, newOuterboundary,offsetvalue)

def calc_R(arraypoints):
    
    Xcoordinatesb, Ycoordinatesb = generatexy (arraypoints)
    Xcoordinates5, Ycoordinates5 = makeOffsetPoly(Xcoordinatesb,Ycoordinatesb, 5)
    
    newOuterboundary = convert_result_check_W(Xcoordinates5, Ycoordinates5)
   
    dividedPoly = polygonDivider(newOuterboundary,20, 1500, 1, True,newOuterboundary)
   
    
    OffsetListdividedPoly = []
    areaPlotfinal = []
    
    finalArea = 0
    for i in dividedPoly:
        
        offsetvalue = 0
        areaPlotvalidR = Area(i)
        Xcoordinatesb, Ycoordinatesb = generatexy (i)
        #check distance of intersectes points and offsets plot if possible
        boundarylengths = lengthBoundary(Xcoordinatesb, Ycoordinatesb)

        while min(boundarylengths) > 10:  
            
            Oldoffset = offsetvalue
                
            offsetvalue += 1
            
            OffsetX, OffsetY = makeOffsetPoly(Xcoordinatesb,Ycoordinatesb,offsetvalue)
            boundarylengths = lengthBoundary(OffsetX, OffsetY)
            #print("boundarylengths", min(boundarylengths))
            
            Points_2_check = convert_into_Points(OffsetX, OffsetY)
            
            if min(OffsetX) == min(Xcoordinatesb) or determine_loop_direction(Points_2_check) == "Counterclockwise":
                
                OffsetX, OffsetY = makeOffsetPoly(Xcoordinatesb, Ycoordinatesb, Oldoffset)
                convertInnerBoundary = convert_result_check_W( OffsetX, OffsetY)
                areaPlotvalidR = Area(convertInnerBoundary)
                print("Oldoffset", Oldoffset)
                offsetvalue = Oldoffset
                break 
        #print("offsetvalue", offsetvalue)

            else: 
                convertInnerBoundary = convert_result_check_W(OffsetX, OffsetY)
                areaPlotvalidR = Area(convertInnerBoundary)

        areaPlotfinal.append(areaPlotvalidR)
        OffsetListdividedPoly.append(offsetvalue)

    areaR = 0
    for area in areaPlotfinal:
        areaR += area
    
    print("areaR", areaR)
    return areaR, dividedPoly, OffsetListdividedPoly

def calc_H(arraypoints):
    
    Xcoordinatesb, Ycoordinatesb = generatexy (arraypoints)
    Xcoordinates5, Ycoordinates5 = makeOffsetPoly(Xcoordinatesb,Ycoordinatesb, 5)
    
    newOuterboundary = convert_result_check_W(Xcoordinates5, Ycoordinates5)
    print("vorher")
    dividedPoly = polygonDivider(newOuterboundary,200, 25000, 1, True,newOuterboundary)
    print("nachher")
    
    OffsetListdividedPoly = []
    areaPlotfinal = []
    
    finalArea = 0
    for i in dividedPoly:
        
        offsetvalue = 0
        areaPlotvalidR = Area(i)
        Xcoordinatesb, Ycoordinatesb = generatexy (i)
        #check distance of intersectes points and offsets plot if possible
        boundarylengths = lengthBoundary(Xcoordinatesb, Ycoordinatesb)

        while min(boundarylengths) > 25:  
            
            Oldoffset = offsetvalue
                
            offsetvalue += 1
            
            OffsetX, OffsetY = makeOffsetPoly(Xcoordinatesb,Ycoordinatesb,offsetvalue)
            boundarylengths = lengthBoundary(OffsetX, OffsetY)
            #print("boundarylengths", min(boundarylengths))
            
            Points_2_check = convert_into_Points(OffsetX, OffsetY)
            
            if min(OffsetX) == min(Xcoordinatesb) or determine_loop_direction(Points_2_check) == "Counterclockwise":
                
                OffsetX, OffsetY = makeOffsetPoly(Xcoordinatesb, Ycoordinatesb, Oldoffset)
                convertInnerBoundary = convert_result_check_W( OffsetX, OffsetY)
                areaPlotvalidR = Area(convertInnerBoundary)
                print("Oldoffset", Oldoffset)
                offsetvalue = Oldoffset
                break 
        #print("offsetvalue", offsetvalue)

            else: 
                convertInnerBoundary = convert_result_check_W(OffsetX, OffsetY)
                areaPlotvalidR = Area(convertInnerBoundary)

        areaPlotfinal.append(areaPlotvalidR)
        OffsetListdividedPoly.append(offsetvalue)

    areaR = 0
    for area in areaPlotfinal:
        areaR += area
    
    print("areaR", areaR)
    return areaR, dividedPoly, OffsetListdividedPoly
    
def calculateFloors (area_all, dict_sorted, max_floors,population):
    
    population_possibleB = area_all//30 
    if population_possibleB >= population:
        #Blockpermiterdevelopment
        number_of_floors = 1 
        for i in dict_sorted.keys():
            dict_sorted[i]['Plotobject'].set_floors(number_of_floors)
            
    
    else: 
        area_all = 0 
        for i in dict_sorted.keys():

            countFloors = 0
            one_floor = dict_sorted[i]['Plotobject'].get_area()
            # print ("one_floor", one_floor, i)
            
            population_possibleB = area_all//30 
            
            while population_possibleB < population and countFloors < max_floors:
                
                area_all += one_floor
                countFloors += 1

                population_possibleB = area_all//30 
                # print ("pop_possible", population_possibleB, countFloors)
            
            dict_sorted[i]['Plotobject'].set_floors(countFloors)
              
   
            if population_possibleB > population:
                break 
    
    return dict_sorted   

def calc(arraypoints, floors, heightperfloor):
    
    a = floors*heightperfloor
    offsetvalue = 0
    
    Xcoordinatesb, Ycoordinatesb = generatexy (arraypoints)

    #check distance of intersectes points and offsets plot if possible
    boundarylengths = lengthBoundary(Xcoordinatesb, Ycoordinatesb) #9

    
    while min(boundarylengths) > 15 and a >= 2:    
        
        Oldoffset = offsetvalue
        #print ("oldlength", oldMinLEngth)
       
        a -= 0.2
        offsetvalue = floors*heightperfloor//a 
        OffsetX, OffsetY = makeOffsetPoly(Xcoordinatesb,Ycoordinatesb,offsetvalue)
        boundarylengths = lengthBoundary(OffsetX, OffsetY)
        
        Points_2_check = convert_into_Points(OffsetX, OffsetY)
        
        if min(OffsetX) == min(Xcoordinatesb) or determine_loop_direction(Points_2_check) == "Counterclockwise":

            return Oldoffset

    return offsetvalue
  
def calc_Eold(arraypoints):
    
    offsetvalue = 0
    Xcoordinatesb, Ycoordinatesb = generatexy (arraypoints)
    #check distance of intersectes points and offsets plot if possible
    boundarylengths = lengthBoundary(Xcoordinatesb, Ycoordinatesb)
    
    while min(boundarylengths) > 20:  
        
        oldMinLEngth = min(boundarylengths)
        Oldoffset = offsetvalue
    
        offsetvalue += 1
        OffsetX, OffsetY = makeOffsetPoly(Xcoordinatesb,Ycoordinatesb,offsetvalue)
        boundarylengths = lengthBoundary(OffsetX, OffsetY)

    if min(boundarylengths) > oldMinLEngth:

        return Oldoffset
    return offsetvalue

def calc_E(arraypoints):
    
    offsetvalue = 0
    Xcoordinatesb, Ycoordinatesb = generatexy (arraypoints)
    #check distance of intersectes points and offsets plot if possible
    boundarylengths = lengthBoundary(Xcoordinatesb, Ycoordinatesb)
    
    while min(boundarylengths) > 20:  
        
        Oldoffset = offsetvalue
        #print("Oldoffset", Oldoffset)
            
        offsetvalue += 1
        OffsetX, OffsetY = makeOffsetPoly(Xcoordinatesb,Ycoordinatesb,offsetvalue)
        boundarylengths = lengthBoundary(OffsetX, OffsetY)
        #print("boundarylengths", min(boundarylengths))
        
        Points_2_check = convert_into_Points(OffsetX, OffsetY)
        
        if min(OffsetX) == min(Xcoordinatesb) or determine_loop_direction(Points_2_check) == "Counterclockwise":
            
            #print("Oldoffset", Oldoffset)
            
            return Oldoffset
    #print("offsetvalue", offsetvalue)
    return offsetvalue
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# PROZESS AND CALLDRAWFUNTION
def G(arraypoints, colorp):
    OffsetX, OffsetY = offsetallplots5(arraypoints)
    #convert x and y lists 
    xCoordAr, yCoordAr = makeFloatfromPoint(OffsetX, OffsetY)
    pleneGGG = plane(xCoordAr,yCoordAr,colorp)
    
    return pleneGGG

    
def R(arraypoints, floors, heightperfloor):

    meshesRfinal = []
    linesRfinal = []
    planeRfinal = []
    
   
    area, dividedboundary, dividedoffset = calc_R(arraypoints)
    
    print("dividedoffset", dividedoffset)

    length = len(dividedboundary)
    
    for i in range(0, length):
        print("i", i)
        xCoordB, yCoordB = generatexy (dividedboundary[i])
        xCoordout,ycoordout = makeFloatfromPoint(xCoordB, yCoordB) 
        
        xCoordsf, yCoordsf = makeOffsetPoly(xCoordB,yCoordB, dividedoffset[i])
        xCoordAr,yCoordAr = makeFloatfromPoint(xCoordsf, yCoordsf) 
    
    #generate list of lines
        IntersectionLines = ListPoint2Lines(xCoordsf, yCoordsf)
        IntersectionLines = numLinesToVec(IntersectionLines)
        #draw_system(IntersectionLines)

        planeR = plane(xCoordout,ycoordout,THREE.Color.new("rgb(174,155,148)"))
        
        
        meshesR, linesR = generateShape(xCoordAr,yCoordAr,THREE.Color.new("rgb(219,208,205)"), THREE.Color.new("rgb(174,155,148)"),floors, heightperfloor)
        
        for j in range(len(meshesR)):
            meshesRfinal.append(meshesR[j])
        
        for k in range(len(linesR)):
            linesRfinal.append(linesR[k])
            
        
        planeRfinal.append(planeR)
        
    print("linesR", linesR)
   
    print ("meshesR", meshesR)
    return meshesRfinal, linesRfinal, planeRfinal

    
def B(arraypoints, colorm, colorl, colorp, floors, heightperfloor):

   
    area, boundary, Offsetv  = calc_B(arraypoints) 
    xCoordB, yCoordB = generatexy (boundary)
    xCoordBF, yCoordBF = makeFloatfromPoint(xCoordB, yCoordB) 
    
    if Offsetv == 0:

        plane1 = plane(xCoordBF, yCoordBF,colorp)
        meshes_listB, lines_listB = generateShape(xCoordBF,yCoordBF,colorm,colorl, floors, heightperfloor )
    
    else:
        
        OffsetX, OffsetY = makeOffsetPoly(xCoordB,yCoordB, Offsetv)
        xCoordAr, yCoordAr = makeFloatfromPoint(OffsetX, OffsetY) 
    
        BlockPermiterLines = ListPoint2Lines(xCoordAr, yCoordAr)
        BlockPermiterLines = numLinesToVec(BlockPermiterLines)
        
        plane1 = plane(xCoordB, yCoordB,colorp)
        meshes_listB, lines_listB = generateShapeblock(xCoordB,yCoordB,colorm,colorl,xCoordAr, yCoordAr, BlockPermiterLines,floors, heightperfloor)
   
    return meshes_listB, lines_listB, plane1

def H(arraypoints, floors, heightperfloor):
    
    meshesRfinal = []
    linesRfinal = []
    planeRfinal = []
    
    
    area, dividedboundary, dividedoffset = calc_H(arraypoints)
    print("dividedboundary", dividedboundary)
    print("dividedoffset", dividedoffset)
    
    
    print("len(dividedboundary)", len(dividedboundary))
    length = len(dividedboundary)
    
    for i in range(0, length):
        print("i", i)
        xCoordB, yCoordB = generatexy (dividedboundary[i])
        xCoordout,ycoordout = makeFloatfromPoint(xCoordB, yCoordB) 
       
        xCoordsf, yCoordsf = makeOffsetPoly(xCoordB,yCoordB, dividedoffset[i])
        xCoordAr,yCoordAr = makeFloatfromPoint(xCoordsf, yCoordsf) 
    
    #generate list of lines
        IntersectionLines = ListPoint2Lines(xCoordsf, yCoordsf)
        IntersectionLines = numLinesToVec(IntersectionLines)
        # draw_system(IntersectionLines)

        planeR = plane(xCoordout,ycoordout,THREE.Color.new("rgb(174,155,148)"))
        print("planeRfinal", planeRfinal)
        print("planeR", planeR)
        
        meshesR, linesR = generateShape(xCoordAr,yCoordAr,THREE.Color.new("rgb(219,208,205)"), THREE.Color.new("rgb(174,155,148)"),4, heightperfloor)
        
        for j in range(len(meshesR)):
            meshesRfinal.append(meshesR[j])
        
        for k in range(len(linesR)):
            linesRfinal.append(linesR[k])
            
        
        planeRfinal.append(planeR)
        
        print("linesR", linesR)
    
        print ("meshesR", meshesR)
        

    
        Offset2X, Offset2Y = makeOffsetPoly(xCoordsf, yCoordsf , 3)
        xCoordAr2, yCoordAr2 = makeFloatfromPoint(Offset2X, Offset2Y)

        meshesTop, linesTop = generateShapeTop(xCoordAr2, yCoordAr2,THREE.Color.new("rgb(219,208,205)"), THREE.Color.new("rgb(174,155,148)"),floors-4, heightperfloor)
        for j in range(len(meshesTop)):
            meshesRfinal.append(meshesTop[j])
        
        for k in range(len(linesTop)):
            linesRfinal.append(linesTop[k])
    print("planeR", planeR)
    return meshesRfinal, linesRfinal, planeRfinal

def E(arraypoints, colorp, colorm, colorl, floors, heightperfloor):

    
    Xcoordinates, Ycoordinates = offsetallplots5(arraypoints)
    newOuterboundary = convert_result_check_W(Xcoordinates, Ycoordinates)

    xCoordB, yCoordB = makeFloatfromPoint( Xcoordinates, Ycoordinates)
    
    offsetvalue = calc_E(newOuterboundary)
    
    OffsetX, OffsetY = makeOffsetPoly(Xcoordinates,Ycoordinates, offsetvalue)

    xCoordAr, yCoordAr = makeFloatfromPoint(OffsetX, OffsetY)

    IntersectionLines = ListPoint2Lines(OffsetX, OffsetY)
    IntersectionLines = numLinesToVec(IntersectionLines)

    plane1 = plane(xCoordB, yCoordB,colorp)
    meshesI, linesI = generateShape(xCoordAr,yCoordAr,colorm, colorl,floors, heightperfloor)
    
    return meshesI, linesI, plane1

def generateTypeL (dict_sorted, offsetR, offsetH, heightperfloorR, heightperfloorB, heightperfloorH, population, density):
    
    calculatetype(dict_sorted, density, population, 11)
    colorm = THREE.Color.new("rgb(219,208,205)")
    colorl = THREE.Color.new("rgb(174,155,148)")
    colorp = THREE.Color.new("rgb(174,155,148)")
    
    meshes_listL = []
    meshes_listH = []
    
    lines_listL = []
    lines_listH = []
    groundes = []
    green = []
    greenP = []
    
    for i in dict_sorted.keys():
            #print("typus", dict_sorted[i]['Plotobject']. get_area_type())
            
            if dict_sorted[i]['Plotobject']. get_area_type() == 0:
                greenP = G(dict_sorted[i]['Plotobject'].get_outerboundary(), THREE.Color.new("rgb(194,204,185)"))
            
            if dict_sorted[i]['Plotobject']. get_area_type() == 1:
                
                meshes_list, lines_list, ground = R(dict_sorted[i]['Plotobject'].get_outerboundary(), 1, heightperfloorR)
            
            elif dict_sorted[i]['Plotobject']. get_area_type() == 2:
                meshes_list, lines_list, ground = R(dict_sorted[i]['Plotobject'].get_outerboundary(), 2, heightperfloorR)
            
            elif dict_sorted[i]['Plotobject']. get_area_type() == 3:
                meshes_list, lines_list, ground = B(dict_sorted[i]['Plotobject'].get_outerboundary(),colorm, colorl, colorp, 3, heightperfloorB)
                
            elif dict_sorted[i]['Plotobject']. get_area_type() == 4:
                meshes_list, lines_list, ground = B(dict_sorted[i]['Plotobject'].get_outerboundary(), colorm,colorl, colorp, 4, heightperfloorB)
            
            elif dict_sorted[i]['Plotobject']. get_area_type() == 5:
                meshes_list, lines_list, ground = B(dict_sorted[i]['Plotobject'].get_outerboundary(), colorm, colorl, colorp,5, heightperfloorB)
            
            elif dict_sorted[i]['Plotobject']. get_area_type() == 6:
                meshes_list, lines_list, ground = B(dict_sorted[i]['Plotobject'].get_outerboundary(), colorm,colorl, colorp, 6, heightperfloorB)
            
            elif dict_sorted[i]['Plotobject']. get_area_type() == 7:
                meshes_list, lines_list, ground = H(dict_sorted[i]['Plotobject'].get_outerboundary(), 7, heightperfloorH)
            
            elif dict_sorted[i]['Plotobject']. get_area_type() == 8:
                meshes_list, lines_list, ground = H(dict_sorted[i]['Plotobject'].get_outerboundary(),  8, heightperfloorH)
            
            elif dict_sorted[i]['Plotobject']. get_area_type() == 9:
                meshes_list, lines_list, ground = H(dict_sorted[i]['Plotobject'].get_outerboundary(),  9, heightperfloorH)
            
            elif dict_sorted[i]['Plotobject']. get_area_type() == 10:
                meshes_list, lines_list, ground = H(dict_sorted[i]['Plotobject'].get_outerboundary(), 10, heightperfloorH)
            
            elif dict_sorted[i]['Plotobject']. get_area_type() == 11:
                meshes_list, lines_list, ground = H(dict_sorted[i]['Plotobject'].get_outerboundary(), 11, heightperfloorH)

            meshes_listL.append(meshes_list)
        
            lines_listL.append(lines_list)
            groundes.append (ground)
            green.append(greenP)
        
            
    return meshes_listL, lines_listL, groundes, green

def offsetAndGenerateShapeO(arraypoints, colorm, colorl, colorp , floors, heightperfloor):
    global scene 
    Xcoordinates, Ycoordinates = offsetallplots5(arraypoints)
    newOuterboundary = convert_result_check_W(Xcoordinates, Ycoordinates)

    xCoordB, yCoordB = makeFloatfromPoint( Xcoordinates, Ycoordinates)
    
    offsetvalue = calc(newOuterboundary, floors, heightperfloor)
    
    OffsetX, OffsetY = makeOffsetPoly(Xcoordinates,Ycoordinates, offsetvalue)

    xCoordAr, yCoordAr = makeFloatfromPoint(OffsetX, OffsetY)

    IntersectionLines = ListPoint2Lines(OffsetX, OffsetY)
    IntersectionLines = numLinesToVec(IntersectionLines)

    plane1 = plane(xCoordB, yCoordB,colorp)
    meshesI, linesI = generateShape(xCoordAr,yCoordAr,colorm, colorl,floors, heightperfloor)
    
    return meshesI, linesI, plane1

def offsetAndGenerateShapeI(arraypoints, offsetvalue, colorm, colorl, colorp , floors, heightperfloor):
    global scene 
    Xcoordinates, Ycoordinates = offsetallplots5(arraypoints)
    newOuterboundary = convert_result_check_W(Xcoordinates, Ycoordinates)

    xCoordB, yCoordB = makeFloatfromPoint( Xcoordinates, Ycoordinates)
    
    
    OffsetX, OffsetY = makeOffsetPoly(Xcoordinates,Ycoordinates, offsetvalue)
    
        

    xCoordAr, yCoordAr = makeFloatfromPoint(OffsetX, OffsetY)

    IntersectionLines = ListPoint2Lines(OffsetX, OffsetY)
    IntersectionLines = numLinesToVec(IntersectionLines)

    plane1 = plane(xCoordB, yCoordB,colorp)
    meshesI, linesI = generateShape(xCoordAr,yCoordAr,colorm, colorl,floors, heightperfloor)
    
    return meshesI, linesI, plane1

def offsetallplots5(arraypoints):
    arraylines = generateLinesNum(arraypoints)
    Plotboundary = numLinesToVec(arraylines)
    
  

    Xcoordinatesb, Ycoordinatesb = generatexy (arraypoints)
    Xcoordinates5, Ycoordinates5 = makeOffsetPoly(Xcoordinatesb,Ycoordinatesb, 5)
    
    return Xcoordinates5, Ycoordinates5
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# DRAW FUNKTIONS THREEJS 
#draw lines 
def draw_system(lines):

    for points in lines:
        line_geom = THREE.BufferGeometry.new()

        points = to_js(points)
        line_geom.setFromPoints( points )
        material = THREE.LineBasicMaterial.new( THREE.Color.new(0x0000ff))
        vis_line = THREE.Line.new( line_geom, material )

        global scene
        scene.add(vis_line)
#draw plane surface        
def plane(xCordsArray,yCordsArray,color):

    shape_Green = THREE.Shape.new()

    for i in range(len(xCordsArray)):
        if i == 0 :
            #("moveTo",xCordsArray[i], yCordsArray[i])
            shape_Green.moveTo (xCordsArray[i], yCordsArray[i])
        else: 
            shape_Green.lineTo(xCordsArray[i], yCordsArray[i])     
    geometryplane = THREE.ShapeGeometry.new(shape_Green)
    
    #colorgreen = 
    meshgreen_material = THREE.MeshPhongMaterial.new(color)
    meshgreen_material.color = color
    meshgreen = THREE.Mesh.new(geometryplane, meshgreen_material)
    meshgreen.receiveShadow = True
    
    # colorS = THREE.Color.new("rgb(180,180,180)")
    # planeMaterial = THREE.ShadowMaterial.new(colorS)
    # planeMaterial.color = colorS
    # plane = THREE.Mesh.new( geometryplane, planeMaterial )
    # plane.receiveShadow = True
    # plane.transparent = True 
    # plane.opacity = 0.5
    
    scene.add(meshgreen)
    # scene.add(plane)
    
    return meshgreen

 
    planeMaterial = THREE.ShadowMaterial.new(color)
    planeMaterial.color = color
    
    plane = THREE.Mesh.new( planeGeometry, planeMaterial )
    
    plane.translateZ(-2)
    plane.transparent = True 
    plane.opacity = 0
    plane.receiveShadow = True
#generate shapes to extrude and cap 
global generateShape

def generateShape(xCordsArray,yCordsArray, color, colorl, floors, heightperfloor,):
    
    global scene
   
    extrudeSettings = {"steps" : 20,"depth" : 3.5,"bevelEnabled": False, "bevelSize": 0 }
    extrudeSettings["depth"] = heightperfloor
    extrudeSettings = Object.fromEntries(to_js(extrudeSettings ))
    
    mesh_list1 = []
    line_list1 = []
    
    for k in range(floors):
        shape_Green = THREE.Shape.new()
    
        for i in range(len(xCordsArray)):
            if i == 0 :
                shape_Green.moveTo (xCordsArray[i], yCordsArray[i])
            else: 
                shape_Green.lineTo(xCordsArray[i], yCordsArray[i])  

        geometry = THREE.ExtrudeGeometry.new(shape_Green,extrudeSettings)
        geometry.translate(0, 0, extrudeSettings.depth*k)
        mesh_material = THREE.MeshPhongMaterial.new(color)
       
        
        mesh_material.color = color
        mesh = THREE.Mesh.new(geometry, mesh_material)
        mesh_list1.append(mesh)
        
        mesh.castShadow = True
        mesh.receiveShadow = False  
        scene.add(mesh)
        
        edgesout = THREE.EdgesGeometry.new( geometry )
        linematerial = THREE.LineBasicMaterial.new( colorl )
        
        linematerial.color = colorl
        line = THREE.LineSegments.new( edgesout, linematerial )
        line_list1.append(line)
   
        scene.add(line)
        
        
    return mesh_list1, line_list1  

def generateShapeTop(xCordsArray,yCordsArray, color, colorl, floors, heightperfloor):


    extrudeSettings = {"steps" : 20,"depth" : 3.5,"bevelEnabled": False, "bevelSize": 0 }
    extrudeSettings["depth"] = heightperfloor
    extrudeSettings = Object.fromEntries(to_js(extrudeSettings ))
    
    linesTop = []
    meshesTop = []
    
    for k in range(floors):
        shape_Green = THREE.Shape.new()
    
        for i in range(len(xCordsArray)):
            if i == 0 :
                shape_Green.moveTo (xCordsArray[i], yCordsArray[i])
            else: 
                shape_Green.lineTo(xCordsArray[i], yCordsArray[i])  

        geometry = THREE.ExtrudeGeometry.new(shape_Green,extrudeSettings)
        geometry.translate(0, 0, extrudeSettings.depth*(k+4))
        mesh_material = THREE.MeshPhongMaterial.new(color)
        # mesh_material.transparent = True
        # mesh_material.opacity = 0.8
        mesh_material.color = color
        mesh = THREE.Mesh.new(geometry, mesh_material)
        mesh.castShadow = True
        mesh.receiveShadow = False  
        meshesTop.append(mesh)
        linematerial = THREE.LineBasicMaterial.new( colorl )
        linematerial.color = colorl
        
        edgesout = THREE.EdgesGeometry.new( geometry )
        line = THREE.LineSegments.new( edgesout, linematerial )
        linesTop.append(line)
        
        global scene
        scene.add(line)
        scene.add(mesh)
    
    return meshesTop,linesTop

def generateShapeblock(xCordsArray,yCordsArray, color, colorl, xCordsHoles, yCordsHoles, array, floors, heightperfloor):

    global scene
    
    extrudeSettings = {"steps" : 20,"depth" : 3.5,"bevelEnabled": False, "bevelSize": 0 }
    extrudeSettings["depth"] = heightperfloor
    extrudeSettings = Object.fromEntries(to_js(extrudeSettings ))
    
    
    linesB = []
    meshesB = []
    
    for k in range(floors):
        
        shape_permit = THREE.Shape.new()
    
        for i in range(len(xCordsArray)):
            if i == 0 :
                shape_permit.moveTo (xCordsArray[i], yCordsArray[i])
            else: 
                shape_permit.lineTo(xCordsArray[i], yCordsArray[i])  
        
        shape_hole = THREE.Shape.new()
        for i in range(len(xCordsHoles)):
            if i == 0 :
                shape_hole.moveTo (xCordsHoles[i], yCordsHoles[i])
            else: 
                shape_hole.lineTo(xCordsHoles[i], yCordsHoles[i])  
        
        shape_permit.holes.push(shape_hole)
        geometry = THREE.ExtrudeGeometry.new(shape_permit,extrudeSettings)
        geometry.translate(0, 0, extrudeSettings.depth*k)
        mesh_material = THREE.MeshPhongMaterial.new(color)
        # mesh_material.transparent = True
        # mesh_material.opacity = 0.8
        mesh_material.color = color
        mesh = THREE.Mesh.new(geometry, mesh_material)
        meshesB.append(mesh)
        mesh.castShadow = True
        mesh.receiveShadow = False  
        
        edgesout = THREE.EdgesGeometry.new( geometry )
        linematerial = THREE.LineBasicMaterial.new( colorl )
        linematerial.color = colorl

        line = THREE.LineSegments.new( edgesout, linematerial )
        linesB.append(line)
        
        global scene
        scene.add(line)
        scene.add(mesh)
    
    
        for points in array:

            points = to_js(points)
        
            shape = THREE.Shape.new(points) 
        
            geometry2 = THREE.ExtrudeGeometry.new(shape,extrudeSettings)
            geometry2.translate(0, 0, extrudeSettings.depth*k)
            mesh_material = THREE.MeshPhongMaterial.new(color)
            mesh_material.lightMap
            # mesh_material.transparent = True
            # mesh_material.opacity = 0.8
            mesh_material.color = color
            mesh2 = THREE.Mesh.new(geometry2, mesh_material)
            meshesB.append(mesh2)
            mesh.castShadow = True
            mesh.receiveShadow = False  
            
            edges = THREE.EdgesGeometry.new( geometry2 )
            
            linematerial = THREE.LineBasicMaterial.new( colorl )
            linematerial.color = colorl

            line = THREE.LineSegments.new( edges, linematerial )
            
            linesB.append(line)
            
            scene.add( line )
            scene.add(mesh2)

    return meshesB, linesB

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#HELPER FUNCTIONS 

def generateLinesNum(listpoints):
        listLines = []
        
        for i in range(len(listpoints)):
            if i < len(listpoints)-1:
                CurrentLine = [listpoints[i], listpoints[i+1]]
                listLines.append(CurrentLine)

            else:
                CurrentLine = [listpoints[i], listpoints[i-(len(listpoints)-1)]]
                listLines.append(CurrentLine)
        return listLines

def generateNumpyArray (plotboundaries):
    temp_list=[]
    Point_list=[]
    for i in plotboundaries:
        for k in i:

            temp_list.append(np.array(k))
        Point_list.append(temp_list)
        temp_list=[]
      
    SUB_SUB_NUMPY = [[np.array(k) * 40 for k in i] for i in plotboundaries]
    # print("biggerscale", SUB_SUB_NUMPY)
    
    return SUB_SUB_NUMPY

def generatexy (arraypoints):
    
    Xcoordinates = []
    Ycoordinates = []

    for m in range(len(arraypoints)):
        Xcoordinates.append(arraypoints[m][0])
        Ycoordinates.append(arraypoints[m][1])
    
    return Xcoordinates, Ycoordinates
     
def makeFloatfromPoint(xlist,ylist):
    fXlist = []
    fyList = []
    for fx in xlist:
        fXlist.append(float(fx))
    for fy in ylist:
        fyList.append(float(fy))
    return fXlist,fyList

def convert_result_check_W(x,y):
    BlockPermiter = []
    for k in range(len(x)): 
        BlockPermiter.append(np.array([x[k], y[k]]))
    return BlockPermiter

def convert_into_Points(x,y):
    BlockPermiter = []
    for k in range(len(x)): 
        BlockPermiter.append([x[k], y[k]])
    return BlockPermiter

def ListPoint2Lines(x,y):

    BlockPermiter = []
    for k in range(len(x)): 
        BlockPermiter.append(np.array([x[k], y[k]]))
        
    lines = []
    for h in range(len(BlockPermiter)):
        if h < len(BlockPermiter)-1:
            CurrentLine = [BlockPermiter[h], BlockPermiter[h+1]]
            lines.append(CurrentLine)

        else:
            CurrentLine = [BlockPermiter[h], BlockPermiter[h-(len(BlockPermiter)-1)]]
            lines.append(CurrentLine)
    return lines

def sort_dict(d, reverse = False):
  return dict(sorted(d.items(), key = lambda x: x[1]['Plotobject'].get_area(), reverse = reverse)) 

def numLinesToVec(ListStartEndpoint): 

        Currentoffset = []
        ListStartEndVec = []

    #offset Shape

        for i in ListStartEndpoint:
            for j in i:
                TempArrayToList = j.tolist()
                ThreeVec1 = THREE.Vector2.new(TempArrayToList[0],TempArrayToList[1])
                Currentoffset.append(ThreeVec1)
            ListStartEndVec.append (Currentoffset)
            Currentoffset = []
        return ListStartEndVec
        
def normalizeVec(x,y):

    distance = np.sqrt(x*x+y*y)
    return x/distance, y/distance

def makeOffsetPoly(oldX, oldY, offset, outer_ccw = 1):
    
    num_points = len(oldX)
    global newX,newY

    newX = []
    newY = []

    for indexpoint in range(num_points):
        prev = (indexpoint + num_points -1 ) % num_points
        next = (indexpoint + 1) % num_points
        vnX =  oldX[next] - oldX[indexpoint]
        vnY =  oldY[next] - oldY[indexpoint]
        vnnX, vnnY = normalizeVec(vnX,vnY)
        nnnX = vnnY
        nnnY = -vnnX
        vpX =  oldX[indexpoint] - oldX[prev]
        vpY =  oldY[indexpoint] - oldY[prev]
        vpnX, vpnY = normalizeVec(vpX,vpY)
        npnX = vpnY * outer_ccw
        npnY = -vpnX * outer_ccw
        bisX = (nnnX + npnX) * outer_ccw
        bisY = (nnnY + npnY) * outer_ccw
        bisnX, bisnY = normalizeVec(bisX,  bisY)
        bislen = offset /  np.sqrt((1 + nnnX*npnX + nnnY*npnY)/2)

        newX.append(oldX[indexpoint] + bislen * bisnX)
        newY.append(oldY[indexpoint] + bislen * bisnY)
        
    points_check = convert_into_Points(newX, newY)
    determine_loop_direction(points_check)
    
    newOuterboundary = convert_result_check_W(newX, newY)
   
    if isSelfIntersect(newOuterboundary) == True:
        # print(newOuterboundary)
        #print("old", oldX, oldY)
        return oldX, oldY
    
    else:
        return newX, newY

def isIntersectingWithoutEndpoints(intersectLinesAsNPList):
    if (np.all(intersectLinesAsNPList[0][0] == intersectLinesAsNPList[1][0]) or np.all(intersectLinesAsNPList[0][0] == intersectLinesAsNPList[1][1]) or 
    np.all(intersectLinesAsNPList[0][1] == intersectLinesAsNPList[1][0]) or np.all(intersectLinesAsNPList[0][1] == intersectLinesAsNPList[1][1])):
        return False
    class Point:
        def __init__(self, x, y):
            self.x = x
            self.y = y


    # Given three collinear points p, q, r, the function checks if
    # point q lies on line segment 'pr'
    def onSegment(p, q, r):
        if ( (q.x <= max(p.x, r.x)) and (q.x >= min(p.x, r.x)) and
            (q.y <= max(p.y, r.y)) and (q.y >= min(p.y, r.y))):
            return True
        return False

    def orientation(p, q, r):
    #Find point orientation
        val = (float(q.y - p.y) * (r.x - q.x)) - (float(q.x - p.x) * (r.y - q.y))
        if (val > 0):
            
            # Clockwise orientation
            return 1
        elif (val < 0):
            
            # Counterclockwise orientation
            return 2
        else:
            
            # Collinear orientation
            return 0

    # The main function that returns true if
    # the line segment 'p1q1' and 'p2q2' intersect.
    def doIntersect(p1,q1,p2,q2):
        
        # Find the 4 orientations required for
        # the general and special cases
        o1 = orientation(p1, q1, p2)
        o2 = orientation(p1, q1, q2)
        o3 = orientation(p2, q2, p1)
        o4 = orientation(p2, q2, q1)

        # General case
        if ((o1 != o2) and (o3 != o4)):
            return True

        # Special Cases

        # p1 , q1 and p2 are collinear and p2 lies on segment p1q1
        if ((o1 == 0) and onSegment(p1, p2, q1)):
            return True

        # p1 , q1 and q2 are collinear and q2 lies on segment p1q1
        if ((o2 == 0) and onSegment(p1, q2, q1)):
            return True

        # p2 , q2 and p1 are collinear and p1 lies on segment p2q2
        if ((o3 == 0) and onSegment(p2, p1, q2)):
            return True

        # p2 , q2 and q1 are collinear and q1 lies on segment p2q2
        if ((o4 == 0) and onSegment(p2, q1, q2)):
            return True

        # If none of the cases
        return False

    TempArrayToList = []
    tempArray1 = []
    for i in intersectLinesAsNPList:
        for j in i:
            tempArray1.append(j.tolist())
        TempArrayToList.append(tempArray1)
        tempArray1 = []

    
    p1 = Point(TempArrayToList[0][0][0],TempArrayToList[0][0][1])
    q1 = Point(TempArrayToList[0][1][0],TempArrayToList[0][1][1])
    p2 = Point(TempArrayToList[1][0][0],TempArrayToList[1][0][1])
    q2 = Point(TempArrayToList[1][1][0],TempArrayToList[1][1][1])
    
    if doIntersect(p1, q1, p2, q2):
        return True
    else:
        return False

def isSelfIntersect(polyVerticesAsNP):
    polyLines = []
    for i in range(len(polyVerticesAsNP)):  #Make the list of polygon vertices into a list of all polygon lines
        if i < len(polyVerticesAsNP)-1:
            CurrentLine = [polyVerticesAsNP[i], polyVerticesAsNP[i+1]]
            polyLines.append(CurrentLine)
        else:
            CurrentLine = [polyVerticesAsNP[i], polyVerticesAsNP[i-(len(polyVerticesAsNP)-1)]]
            polyLines.append(CurrentLine)
    for i in polyLines:
        for j in polyLines: #test if inputline runs through base shape (for every boundary line of base shape) despite endpoints beeing outside
            if all(np.array_equal(i[o], j[o]) for o in range(len(i))):
                continue
            testLines = [i,j]
            if isIntersectingWithoutEndpoints(testLines) == True:
                return True
    return False

# print(isSelfIntersect([np.array([0,0]),np.array([10,0]),np.array([10,10]),np.array([0,10]),np.array([11,5])]))
             
def lengthBoundary(xcoord, ycoord):
    #print("xcoordoffset", xcoord)

    global LengthList
    LengthList = []

    for i in range(len(xcoord)-1):
        length = np.sqrt((xcoord[i]-xcoord[i+1])**2 + ((ycoord[i]-ycoord[i+1])**2))
        LengthList.append(length)
    
    return LengthList

def loop_check_angle(arraypoints):
    arraylines = generateLinesNum(arraypoints)
    
    
    for current_line in arraylines: 
        print(current_line[0])
        
        startline = current_line[0]
        print("startline", startline)
        next_line = current_line[1]
        
        angle = calculate_angle(startline, next_line)
        print ("angle" , math.degrees(angle))
        
        if math.degrees(angle) > 90:
            arraylines.pop(current_line[0])  
            # arraylines.remove(next_line) 
               
    
    #print ("arraylines", arraylines)
    return arraylines


#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


def determine_loop_direction(points):
    n = len(points)
    x = [p[0] for p in points]
    y = [p[1] for p in points]
    a = sum(x[i]*y[(i+1)%n] - x[(i+1)%n]*y[i] for i in range(n))
    return "Counterclockwise" if a > 0 else "Clockwise"

##########################################################################################
def calculate_angle(line1, line2):
    x1, y1 = line1[1][0] - line1[0][0], line1[1][1] - line1[0][1]
    x2, y2 = line2[1][0] - line2[0][0], line2[1][1] - line2[0][1]
    return math.atan2(x1*y2 - y1*x2, x1*x2 + y1*y2)
##########################################################################################
def sharpest_right_turn(angles):
    
    angles_in_radians = [math.radians(angle) for angle in angles]
    right_turn_angles = []
    for i in range(len(angles_in_radians)):
        right_turn_angles.append(angles_in_radians[i])
    max_turn_index = right_turn_angles.index(min(right_turn_angles))
    return max_turn_index

def loop_finder(INPUT_LINES):

    """
    Given a list of lines represented as pairs of points, this function finds all loops in the lines.
    A loop is defined as a series of lines where the endpoint of one line is the startpoint of the next line, and the endpoint of the last line is the startpoint of the first line.
    The function returns a list of loops, with each loop represented as a list of points in the order they are encountered in the loop.
    :param INPUT_LINES: list of lines represented as pairs of points
    :return: list of loops, each represented as a list of points
    """
    Loops=[]
    
    for current_line in INPUT_LINES: 
        Loop=[]
        Loop.append(current_line[0])
        Loop.append(current_line[1])

        connecting_lines=[]
        flipped_connector=[]
        # line is  a connecting line, but not itself
        
        for line in INPUT_LINES:
            if line [0] == current_line[1] and line != current_line:
                connecting_lines.append(line)
            if line [1] == current_line[1] and line != current_line:
                flipped_connector=[]
                flipped_connector.append(line[1])
                flipped_connector.append(line[0])
                connecting_lines.append(flipped_connector)
            
        

        if len(connecting_lines) >=1:
            connecting_angles = []
            for neigbhor in connecting_lines:
                angle = calculate_angle(current_line, neigbhor)           
                connecting_angles.append(math.degrees(angle))
            next_line_index= sharpest_right_turn(connecting_angles)
            next_line = connecting_lines[next_line_index]
            Loop.append(next_line[1])
        
        while Loop[-1] != Loop[0]:
            
            Next_connecting_lines=[]
            for line in INPUT_LINES:  
                if line == next_line or line[1] == next_line[0] and line[0] == next_line[1]:
                    pass
                else:
                    if line [0] == Loop[-1] :
                            Next_connecting_lines.append(line)
                    
                    if line [1] == Loop[-1] :
                            flipped_connector=[]
                            flipped_connector.append(line[1])
                            flipped_connector.append(line[0])
                            Next_connecting_lines.append(flipped_connector)

            
            if len(Next_connecting_lines) >=1:
                next_connecting_angles =[]
                for next_neigbhor in Next_connecting_lines:
                    angle = calculate_angle(next_line, next_neigbhor)           
                    next_connecting_angles.append(math.degrees(angle))
                next_line_index= sharpest_right_turn(next_connecting_angles)
                next_line = Next_connecting_lines[next_line_index]
                Loop.append(next_line[1])
                if Loop.count(next_line[1]) == 2:
                    break
            else:
                Loop=[]
                break
        if len(Loop) >=1:    
            Loop.pop(-1)   #delete double coordinate

        direction = determine_loop_direction(Loop)
        if direction== "Clockwise":
            if len(Loop) >=1:  
                Loops.append(Loop)
        if direction== "Counterclockwise":
            Loop=[]
            FlippedStart=[]
            FlippedStart.append(current_line[1])
            FlippedStart.append(current_line[0])
            INPUT_LINES.append(FlippedStart)
            
    new_loops = []
    for sublist in Loops:
        is_duplicate = False
        for other_sublist in new_loops:
            if set(map(tuple,sublist)) <= set(map(tuple,other_sublist)):
                is_duplicate = True
                break
        if not is_duplicate:
            new_loops.append(sublist)
    Loops = new_loops              #Loops is now the cleaned up version of itself




    return Loops

##########################################################################################
def find_overlapping_plots(plots):
    # Create a dictionary to store the mapping from plot number to overlapping plots
    plot_overlaps = {}
    # Iterate over each plot
    for i, plot in enumerate(plots):
        # Initialize an empty list to store the overlapping plots for this plot
        overlaps = []
        # Iterate over the other plots
        for j, other_plot in enumerate(plots):
            # Skip the current plot
            if i == j:
                continue
            # Check if the current plot has 2 or more coordinates in common with the other plot
            common_coords = set(plot).intersection(set(other_plot))
            if len(common_coords) >= 2:
                overlaps.append(j)
        # Add the mapping from plot number to overlapping plots to the dictionary
        plot_overlaps[i] = overlaps
    # Create a list of tuples (plot number, overlapping plots) from the dictionary
    result = [(plot, overlaps) for plot, overlaps in plot_overlaps.items()]
    return result
##########################################################################################
def convert_data(list_neighbours: list[list[int, list[int]]]) -> dict:
    """
    Converts the data from a list to a dictionary.
    """
    # Initialize the dictionary
    dictionary = {}

    # Loop through the plots
    for plot, neighbours in list_neighbours:

        # Add the plot to the dictionary
        dictionary[plot] = {'value': None, 'neighbours': neighbours}
    return dictionary
##########################################################################################
def random_distribution(dictionary: dict) -> dict:
    
    """
    Randomly assign a value to each plot and checks if the rules are
    respected.
    """
    # Declare the possible values
    weights=[]
    modified_val_l = 110-input_param.LivingIndustrial
    weights.append(modified_val_l)
    modified_val_i = input_param.LivingIndustrial
    weights.append(modified_val_i)
    modified_val_g = (110-input_param.LivingIndustrial+55)/2
    weights.append(modified_val_g)
    modified_val_o = (input_param.LivingIndustrial+55)/2
    if modified_val_o<55:
        modified_val_o=modified_val_o/2 
    weights.append(modified_val_o)
    modified_val_e = 100
    weights.append(modified_val_e)
    
    values = ['L', 'I', 'G', 'O', 'E']
    #weights = [20, 20, 20, 20, 20]
    L_Count=0
    I_Count=0
    G_Count=0
    O_Count=0
    E_Count=0
    
    # Get the first plot in the dictionary
    first_plot = list(dictionary.keys())[0]

    # Choose a random value from the list of possible values
    value = choice(['L', 'I', 'G', 'O', 'E'])
    VALID_VALUES=[]
    # Assign the random value to the first plot and change possible Neighbor Values accordingly
    dictionary[first_plot]['value'] = value
    combined_plots = {}
    for neighbor in dictionary[first_plot]['neighbours']:
        if dictionary[first_plot]['value'] == 'L':
                        while "I" in values:
                            index= values.index("I")
                            if index < len(values):
                                values.pop(index)
                                weights.pop(index)
        elif dictionary[first_plot]['value'] == 'I':
            while "L" in values:
                index= values.index("L")
                if index < len(values):
                    values.pop(index)
                    weights.pop(index)
            while "E" in values:
                index= values.index("E")
                if index < len(values):
                    values.pop(index)
                    weights.pop(index)
        #elif dictionary[first_plot]['value'] == 'G':
            # while "G" in values:
            #     index= values.index("G")
            #     if index < len(values):
            #         values.pop(index)
            #         weights.pop(index)
        if L_Count >= 4:
            while "L" in values:
                index= values.index("L")
                if index < len(values):
                    values.pop(index)
                    weights.pop(index)
        if I_Count >= 4:
            while "I" in values:
                index= values.index("I")
                if index < len(values):
                    values.pop(index)
                    weights.pop(index)
        if G_Count >= 4:
            while "G" in values:
                index= values.index("G")
                if index < len(values):
                    values.pop(index)
                    weights.pop(index)
        if O_Count >= 4:
            while "O" in values:
                index= values.index("O")
                if index < len(values):
                    values.pop(index)
                    weights.pop(index)
        if E_Count >= input_param.population//3000:
            while "E" in values:
                index= values.index("E")
                if index < len(values):
                    values.pop(index)
                    weights.pop(index)

        
        
        valid_vals= ([neighbor],values,weights)
        VALID_VALUES.append(valid_vals)
    VALID_VALUES_NO_DOUBLES = []
        
            
    visited=[0]

    if value=="L":
        L_Count=L_Count+1                    
        
    elif value=="I":
        I_Count=I_Count+1
        
    elif value=="G":
        G_Count=G_Count+1
        
    elif value=="O":
        O_Count=O_Count+1
        
    elif value=="E":
        E_Count=E_Count+1
    
    
    for i in VALID_VALUES:
                if i not in VALID_VALUES_NO_DOUBLES:
                    VALID_VALUES_NO_DOUBLES.append(i)
    for plot in VALID_VALUES_NO_DOUBLES:
            plot_num, possible_values, weights = plot
            plot_num = plot_num[0]
            indices = range(len(possible_values))
            if plot_num in combined_plots:
                current_values, current_weights= combined_plots[plot_num]
                combined_values = set(current_values) & set(possible_values)
                combined_indices = [i for i in indices if possible_values[i] in combined_values]
                combined_weights = [weights[i] for i in combined_indices]
                combined_plots[plot_num] = (list(combined_values), combined_weights)
            else:
                combined_plots[plot_num] = (possible_values, weights)
    combined_plots = {key: value for key, value in combined_plots.items() if key not in visited}
    sorted_dict = dict(sorted(combined_plots.items(), key=lambda x: len(x[1][0])))
    
    # Assign the value to the plot
    # dictionary[neighbor]['value'] = value

    values = ['L', 'I', 'G', 'O', 'E']
    # Declare the possible values
    weights=[]
    modified_val_l = 110-input_param.LivingIndustrial
    weights.append(modified_val_l)
    modified_val_i = input_param.LivingIndustrial
    weights.append(modified_val_i)
    modified_val_g = (110-input_param.LivingIndustrial+55)/2
    weights.append(modified_val_g)
    modified_val_o = (input_param.LivingIndustrial+55)/2
    if modified_val_o<55:
        modified_val_o=modified_val_o/2 
    weights.append(modified_val_o)
    modified_val_e = 100
    weights.append(modified_val_e)
    #weights = [20, 20, 20, 20, 20]
        
    

    
    # plots_sorted = []
    # for plot in dictionary.keys():
    #     remaining_values = 5 - len(values)
    #     plots_sorted.append((plot, remaining_values))
    # plots_sorted.sort(key=lambda x: x[1])
    #print("PLOTS_SORTED_WEIRD",sorted_dict)
    

    # Loop through the plots
    while combined_plots != {}:
        for plot in sorted_dict:
            if plot>0:
                visited.append(plot)
                
                # Check the values of the neighbors
                for neighbor in dictionary[plot]['neighbours']:
                    # if dictionary[neighbor]['value'] == 'G':
                    #     while "G" in values:
                    #         index= values.index("G")
                    #         if index < len(values):
                    #             values.pop(index)
                    #             weights.pop(index)
                    # elif dictionary[neighbor]['value'] == 'C':
                    #     while "I" in values:
                    #         index= values.index("I")
                    #         if index < len(values):
                    #             values.pop(index)
                    #             weights.pop(index)
                    if dictionary[neighbor]['value'] == 'L':
                        while "I" in values:
                            index= values.index("I")
                            if index < len(values):
                                values.pop(index)
                                weights.pop(index)
                    elif dictionary[neighbor]['value'] == 'I':
                        while "L" in values:
                            index= values.index("L")
                            if index < len(values):
                                values.pop(index)
                                weights.pop(index)
                        # while "C" in values:
                        #     index= values.index("C")
                        #     if index < len(values):
                        #         values.pop(index)
                        #         weights.pop(index)
                        # while "P" in values:
                        #     index= values.index("P")
                        #     if index < len(values):
                        #         values.pop(index)
                        #         weights.pop(index)
                    elif dictionary[neighbor]['value'] == 'E':
                        while "I" in values:
                            index= values.index("I")
                            if index < len(values):
                                values.pop(index)
                                weights.pop(index)
                    if L_Count >= 4:
                        while "L" in values:
                            index= values.index("L")
                            if index < len(values):
                                values.pop(index)
                                weights.pop(index)
                    if I_Count >= 4:
                        while "C" in values:
                            index= values.index("I")
                            if index < len(values):
                                values.pop(index)
                                weights.pop(index)
                    if G_Count >= 4:
                        while "G" in values:
                            index= values.index("G")
                            if index < len(values):
                                values.pop(index)
                                weights.pop(index)
                    if O_Count >= 4:
                        while "O" in values:
                            index= values.index("O")
                            if index < len(values):
                                values.pop(index)
                                weights.pop(index)
                    if E_Count >= input_param.population//3000:
                        while "E" in values:
                            index= values.index("E")
                            if index < len(values):
                                values.pop(index)
                                weights.pop(index)
                
                    
                    valid_vals= ([neighbor],values,weights)
                    VALID_VALUES.append(valid_vals)

            # Assign a value to the plot, using weighted probability
            if(len(values))>=1:
                value = choices(values, weights=weights, k=1)[0]
                
                # Assign the value to the plot
                dictionary[plot]['value'] = value
                

            else:
                for plot in dictionary.keys():
                    # Set the value to None
                    
                    dictionary[plot]['value'] = None
                return False 
            
            for i in VALID_VALUES: ###################################################### List operations for combining different possibilities when checking from a different neigbor
                    if i not in VALID_VALUES_NO_DOUBLES:
                        VALID_VALUES_NO_DOUBLES.append(i)
            for plot in VALID_VALUES_NO_DOUBLES:
                    plot_num, possible_values, weights = plot
                    plot_num = plot_num[0]
                    indices = range(len(possible_values))
                    if plot_num in combined_plots:
                        current_values, current_weights= combined_plots[plot_num]
                        combined_values = set(current_values) & set(possible_values)
                        combined_indices = [i for i in indices if possible_values[i] in combined_values]
                        combined_weights = [weights[i] for i in combined_indices]
                        combined_plots[plot_num] = (list(combined_values), combined_weights)
                    else:
                        combined_plots[plot_num] = (possible_values, weights)
            values = ['L', 'I', 'G', 'O', 'E']    ##############################reset weights and Values
            # Declare the possible values
            weights=[]
            modified_val_l = 110-input_param.LivingIndustrial
            weights.append(modified_val_l)
            modified_val_i = input_param.LivingIndustrial
            weights.append(modified_val_i)
            modified_val_g = (110-input_param.LivingIndustrial+55)/2
            weights.append(modified_val_g)
            modified_val_o = (input_param.LivingIndustrial+55)/2
            if modified_val_o<55:
                modified_val_o=modified_val_o/2    
            weights.append(modified_val_o)
            modified_val_e = 100
            weights.append(modified_val_e)
                    
            #weights = [20, 20, 20, 20, 20]
                    
            combined_plots_all = {key: value for key, value in combined_plots.items()}################################# A list with all possible values for all Plots
            sorted_dict_all = dict(sorted(combined_plots_all.items(), key=lambda x: len(x[1][0])))
            #print("Options_if_changes_neccessary:",sorted_dict_all)       
            
            combined_plots = {key: value for key, value in combined_plots.items() if key not in visited}############### A list with all possible values for all Plots that havnt been assigned yet
            sorted_dict = dict(sorted(combined_plots.items(), key=lambda x: len(x[1][0])))
            
            ############### Count the assignment Values
            if value=="L":  
                L_Count=L_Count+1                    
                
            elif value=="I":
                I_Count=I_Count+1
                
            elif value=="G":
                G_Count=G_Count+1
                
            elif value=="O":
                O_Count=O_Count+1
                
            elif value=="E":
                E_Count=E_Count+1
   
    print("LCount",L_Count)
    print("ICount",I_Count)  
    print("GCount",G_Count)  
    print("OCount",O_Count)  
    print("ECount",E_Count)  
    # print(C_Count)     
    # print(R_Count) 
    # print(I_Count) 
    # print(P_Count)
    #print("visited",visited)
    return dictionary, sorted_dict_all
##########################################################################################
def find_solution(dictionary: dict,
                max_time: float = 30) -> dict:
    """
    Generates solutions until a valid one is found or the time limit.
    is reached.
    """
    # Initialize the answer and the time
    answer, start = {}, time()

    # Set the stopping condition
    while answer == {} and (time() - start) < max_time:

        # Get a potential solution
        answer = random_distribution(dictionary)

    if answer == False:
        find_solution(dictionary,5)
    else:
        return answer
##########################################################################################
##########################################################################################
def polygonDivider(inputPolygonsAsNp,minSize = 0, maxSize = 250000, H_or_V = 1, mustHaveStreetConnection = False,streetToConnectToAsNPVertices = [], randomizeH_V = False, force_H = False, force_V = False,min_compactness = 0, finishedPolygons = [],percentageOfCut = 50, count = 0, turnCount = 0):
    #Explanation of polygon input:
    #InputPolygonsAsNp: The Polygon you want to subdivide. Geometry should be displayed as a list with the vertices of the polygon in it in the form of np-vectors
    #minSize: The minimal size a generated plot is allowed to have
    #maxSize: the maximal size a generated plot is allowed to have (not guaranteed to always be smaller than this)
    #H_or_V: You can, but don't have to, decide wether to start by slicing horizontally or Vertically, 0: Slizes Vertical, 1: Slizes horizontal
    #MustHaveStreetConnection: True or False, decides wether all newly generated plots have to share a side with the initial polygon
    #streetToConnectToAsNPVertices: MANDATORY to include if MustHaveStreetConnection is = True! The Initial Polygon that all newly created polygons are supposed to share an edge with
    #randomizeH_V: Put True to let the function randomize with each iteration if the polygons are slized vertically or horizontally
    #Force_H/Force_V: Forces the desired direction, no other direction will be used for the split
    #min_compactness: number between 0-1 that defines the required compactness of the generated Plots. NOT IMPLEMENTED YET

    if len(inputPolygonsAsNp) == 0:
        return finishedPolygons
    if type(inputPolygonsAsNp[0]) != list:      #Unify data-structure
        inputPolygonsAsNp = [inputPolygonsAsNp.copy()]
    H_or_V += 1

    if force_V == True:     #Create Possibility to force algorhythm to only cut in one direction
        cutDir = "V"
    elif force_H == True:
        cutDir = "H"
    elif randomizeH_V == True:
        numb = random.randint(0,1)
        if numb == 0:
            cutDir = "V"
        else:
            cutDir = "H"
    elif H_or_V % 2:
        cutDir = "V"
    else:
        cutDir = "H"

    if count > 10:       #if algorythm tries too often it stops automatically
        return inputPolygonsAsNp

    currentFinishedPolys = []
    for i in finishedPolygons:
        currentFinishedPolys.append(i)
    
    currentPoly = []
    for i in inputPolygonsAsNp:
        currentPoly.append(i)

    
    for i in range(len(currentPoly)):   #   For every "open" polygon that still needs processing
        splitPoly = polygonSplit(currentPoly[i],cutDir,percentageOfCut)
        
        print("splitPoly", splitPoly)
        if type(splitPoly) is str:
            if count <= 5:
                count += 1
                return polygonDivider(currentPoly, minSize, maxSize, H_or_V, mustHaveStreetConnection ,streetToConnectToAsNPVertices , randomizeH_V , force_H , force_V ,min_compactness , currentFinishedPolys,percentageOfCut-(percentageOfCut/5) , count , turnCount)
            
            else:
                inputPolygonsAsNp.pop(i)
                return polygonDivider(currentPoly, minSize, maxSize, H_or_V, mustHaveStreetConnection ,streetToConnectToAsNPVertices , randomizeH_V , force_H , force_V ,min_compactness , currentFinishedPolys,percentageOfCut , count , turnCount)
        
        newLeftPolys = splitPoly[0]
        newRightPolys = splitPoly[1]
        leftArea = []
        rightArea = []
        for j in newLeftPolys:
            area = NumpyArea(j)
            if area > maxSize:
                leftArea.append("Too Big")
                continue
            elif area < minSize:
                leftArea.append("Too Small")
                continue
            else:
                leftArea.append("Right")

        for j in newRightPolys:
            area = NumpyArea(j)
            if area > maxSize:
                rightArea.append("Too Big")
                continue
            elif area < minSize:
                rightArea.append( "Too Small")
                continue
            else:
                rightArea.append("Right")
        leftCompactness = []
        rightCompactness = []
        for k in newLeftPolys:
            perimeter = 0
            polygonLines = []
            for c in range(len(k)):   #Convert Polygon to lines
                if c < len(k)-1:
                    CurrentLine = [k[c], k[c+1]]
                    polygonLines.append(CurrentLine)
                else:
                    CurrentLine = [k[c], k[c-(len(k)-1)]]
                    polygonLines.append(CurrentLine)
            for s in polygonLines:
                perimeter += np.linalg.norm(s[1]-s[0])
            compactness = 4 * np.pi * NumpyArea(k) / perimeter ** 2
            if compactness >= min_compactness:
                leftCompactness.append(True)
            else:
                leftCompactness.append(False)

        for k in newRightPolys:
            perimeter = 0
            polygonLines = []
            for c in range(len(k)):   #Convert Polygon to lines
                if c < len(k)-1:
                    CurrentLine = [k[c], k[c+1]]
                    polygonLines.append(CurrentLine)
                else:
                    CurrentLine = [k[c], k[c-(len(k)-1)]]
                    polygonLines.append(CurrentLine)
            for s in polygonLines:
                perimeter += np.linalg.norm(s[1]-s[0])
            compactness = 4 * np.pi * NumpyArea(k) / perimeter ** 2
            if compactness >= min_compactness:
                rightCompactness.append(True)
            else:
                rightCompactness.append(False)

        if any(leftCompactness) == False or any(rightCompactness) == False:
            if turnCount % 2:
                if cutDir == "H":
                    turnCount += 1  
                    return polygonDivider(currentPoly, minSize, maxSize, 1, mustHaveStreetConnection ,streetToConnectToAsNPVertices , False , force_H , force_V ,min_compactness , currentFinishedPolys,percentageOfCut , count , turnCount)
                else:
                    turnCount += 1  
                    return polygonDivider(currentPoly, minSize, maxSize, 2, mustHaveStreetConnection ,streetToConnectToAsNPVertices , False , force_H , force_V ,min_compactness , currentFinishedPolys,percentageOfCut , count , turnCount)
            

        if mustHaveStreetConnection == True:        #If required checks if new polygons connect to streets

            if any(y == "Too Small" for y in leftArea) and any(y == "Too Small" for y in rightArea): #Dividing the Polygon return areas too small, mark undivided polygon as finished
                turnCount = 0
                count = 0
                currentFinishedPolys.append(currentPoly[i])
                currentPoly.pop(i)
                return polygonDivider(currentPoly, minSize, maxSize, H_or_V, mustHaveStreetConnection ,streetToConnectToAsNPVertices , randomizeH_V , force_H , force_V ,min_compactness , currentFinishedPolys,percentageOfCut , count , turnCount)

            connectStreetLines = []
            for c in range(len(streetToConnectToAsNPVertices)):   #Convert Polygon to lines
                if c < len(streetToConnectToAsNPVertices)-1:
                    CurrentLine = [streetToConnectToAsNPVertices[c], streetToConnectToAsNPVertices[c+1]]
                    connectStreetLines.append(CurrentLine)
                else:
                    CurrentLine = [streetToConnectToAsNPVertices[c], streetToConnectToAsNPVertices[c-(len(streetToConnectToAsNPVertices)-1)]]
                    connectStreetLines.append(CurrentLine)
            streetConLeft = []
            streetConRight = []

            for k in newLeftPolys:  #check if Left Polygon(s) connect to street
                tempOnline = 0
                for y in k:
                    if pointOnPolygon(y,connectStreetLines) == True:
                        tempOnline += 1
                if tempOnline >= 2:
                    streetConLeft.append(True)
                else:
                    streetConLeft.append(False)
 
            for k in newRightPolys:     #check if Right Polygon(s) connect to street
                tempOnline = 0
                for y in k:
                    if pointOnPolygon(y,connectStreetLines) == True:
                        tempOnline += 1
                if tempOnline >= 2:
                    streetConRight.append(True)
                else:
                    streetConRight.append(False)
            
            if all(streetConLeft) == False and all(streetConRight) == False:        #Further divison of current polygon not possible, mark undivided polygon as finished
                turnCount = 0
                count = 0
                currentFinishedPolys.append(currentPoly[i])
                currentPoly.pop(i)
                return polygonDivider(currentPoly, minSize, maxSize, H_or_V, mustHaveStreetConnection ,streetToConnectToAsNPVertices , randomizeH_V , force_H , force_V ,min_compactness , currentFinishedPolys,percentageOfCut , count , turnCount)

            elif any(streetConLeft) == False or any(streetConRight) == False:
                if count <=5:
                    count += 1
                    if turnCount % 2:
                        if cutDir == "H":
                            turnCount += 1  
                            return polygonDivider(currentPoly, minSize, maxSize, 1, mustHaveStreetConnection ,streetToConnectToAsNPVertices , False , force_H , force_V ,min_compactness , currentFinishedPolys,percentageOfCut , count , turnCount)
                        else:
                            turnCount += 1  
                            return polygonDivider(currentPoly, minSize, maxSize, 2, mustHaveStreetConnection ,streetToConnectToAsNPVertices , False , force_H , force_V ,min_compactness , currentFinishedPolys,percentageOfCut , count , turnCount)
                        
                    else:
                        turnCount = 0
                        count = 0
                        currentFinishedPolys.append(currentPoly[i])
                        currentPoly.pop(i)
                        return polygonDivider(currentPoly, minSize, maxSize, H_or_V, mustHaveStreetConnection ,streetToConnectToAsNPVertices , randomizeH_V , force_H , force_V ,min_compactness , currentFinishedPolys,percentageOfCut , count , turnCount)
                else:
                    turnCount = 0
                    count = 0
                    currentFinishedPolys.append(currentPoly[i])
                    currentPoly.pop(i)
                    return polygonDivider(currentPoly, minSize, maxSize, H_or_V, mustHaveStreetConnection ,streetToConnectToAsNPVertices , randomizeH_V , force_H , force_V ,min_compactness , currentFinishedPolys,percentageOfCut , count , turnCount)
                
            elif all(streetConLeft) == True and all(streetConRight) == True:        #Condition met: All New Polygons have street-access
                if all(y == "Right" for y in leftArea) and all(y == "Right" for y in rightArea):    #Perfectly finishes: Area is correct and Plots connect to streets
                    for x in newLeftPolys:
                        currentFinishedPolys.append(x)
                    for x in newRightPolys:
                        currentFinishedPolys.append(x)
                    count = 0
                    turnCount = 0
                    currentPoly.pop(i)
                    return polygonDivider(currentPoly, minSize, maxSize, H_or_V, mustHaveStreetConnection ,streetToConnectToAsNPVertices , randomizeH_V , force_H , force_V ,min_compactness , currentFinishedPolys,percentageOfCut , count , turnCount)
                elif  all(y == "Too Big" for y in leftArea) and all(y == "Too Big" for y in rightArea):       #Both sides Valid, but have to be divided further
                    if count <= 5:
                        currentPoly.pop(i)
                        for x in newRightPolys:
                            currentPoly.insert(0, x)
                        for x in newLeftPolys:
                            currentPoly.insert(0, x)
                        count += 1
                        return polygonDivider(currentPoly, minSize, maxSize, H_or_V, mustHaveStreetConnection ,streetToConnectToAsNPVertices , randomizeH_V , force_H , force_V ,min_compactness , currentFinishedPolys,percentageOfCut , count , turnCount)
                    else:
                        turnCount = 0
                        count = 0
                        currentFinishedPolys.append(currentPoly[i])
                        currentPoly.pop(i)
                        return polygonDivider(currentPoly, minSize, maxSize, H_or_V, mustHaveStreetConnection ,streetToConnectToAsNPVertices , randomizeH_V , force_H , force_V ,min_compactness , currentFinishedPolys,percentageOfCut , count , turnCount)

                elif all(y == "Too Small" for y in leftArea) == False and any(y == "Too Small" for y in rightArea) == False:  #Two sides are not all perfect, but none is too small
                    if count <= 5:
                        for z in range(len(newLeftPolys)):
                            if leftArea[z] == "Right":
                                currentFinishedPolys.append(newLeftPolys[z])
                                del newLeftPolys[z]
                        for z in range(len(newRightPolys)):
                            if rightArea[z] == "Right":
                                currentFinishedPolys.append(newRightPolys[z])
                                del newRightPolys[z]
                        currentPoly.pop(i)
                        for x in newRightPolys:
                            currentPoly.insert(0, x)
                        for x in newLeftPolys:
                            currentPoly.insert(0, x)
                        count += 1
                        return polygonDivider(currentPoly, minSize, maxSize, H_or_V, mustHaveStreetConnection ,streetToConnectToAsNPVertices , randomizeH_V , force_H , force_V ,min_compactness , currentFinishedPolys,percentageOfCut , count , turnCount)
                    else:
                        turnCount = 0
                        count = 0
                        currentFinishedPolys.append(currentPoly[i])
                        currentPoly.pop(i)
                        return polygonDivider(currentPoly, minSize, maxSize, H_or_V, mustHaveStreetConnection ,streetToConnectToAsNPVertices , randomizeH_V , force_H , force_V ,min_compactness , currentFinishedPolys,percentageOfCut , count , turnCount)

                elif  any(y == "Too Small" for y in leftArea) == False and any(y == "Too Small" for y in rightArea):
                    
                    if count <= 5:
                        count += 1
                        return polygonDivider(currentPoly, minSize, maxSize, H_or_V, mustHaveStreetConnection ,streetToConnectToAsNPVertices , randomizeH_V , force_H , force_V ,min_compactness , currentFinishedPolys,percentageOfCut-(percentageOfCut/2) , count , turnCount)
                    else:
                        turnCount = 0
                        count = 0
                        currentFinishedPolys.append(currentPoly[i])
                        currentPoly.pop(i)
                        return polygonDivider(currentPoly, minSize, maxSize, H_or_V, mustHaveStreetConnection ,streetToConnectToAsNPVertices , randomizeH_V , force_H , force_V ,min_compactness , currentFinishedPolys,percentageOfCut , count , turnCount)

                elif  any(y == "Too Small" for y in leftArea) and any(y == "Too Small" for y in rightArea) == False:
                    
                    if count <= 5:
                        count += 1
                        return polygonDivider(currentPoly, minSize, maxSize, H_or_V, mustHaveStreetConnection ,streetToConnectToAsNPVertices , randomizeH_V , force_H , force_V ,min_compactness , currentFinishedPolys,percentageOfCut+((-(percentageOfCut)+100)/2)/count , count , turnCount)
                    else:
                        turnCount = 0
                        count = 0
                        currentFinishedPolys.append(currentPoly[i])
                        currentPoly.pop(i)
                        return polygonDivider(currentPoly, minSize, maxSize, H_or_V, mustHaveStreetConnection ,streetToConnectToAsNPVertices , randomizeH_V , force_H , force_V ,min_compactness , currentFinishedPolys,percentageOfCut-(percentageOfCut/2)/count , count , turnCount)



        count += 1
        return polygonDivider(currentPoly, minSize, maxSize, H_or_V, mustHaveStreetConnection ,streetToConnectToAsNPVertices , randomizeH_V , force_H , force_V ,min_compactness , currentFinishedPolys,percentageOfCut , count , turnCount)

def NumpyArea(verticesAsNP):

    n = len(verticesAsNP) # of verticesAsNP
    area = 0

    for i in range(n):
        j = (i + 1) % n
        area += (verticesAsNP[i][0] * verticesAsNP[j][1])
        area -= (verticesAsNP[j][0] * verticesAsNP[i][1])
    area = abs(area)/2.0

    return area

def arrayIndex(arrayList,searchedArray):
    for i in range(len(arrayList)):
        if np.all(searchedArray == arrayList[i]):
            return i

def minimalBoundingBox(pointsOfPolyAsNP): #Find the minimum bounding box for an polygon, Output is always clockwise! (at least never encountered different)
    
    pointsOfPoly = []
    for i in pointsOfPolyAsNP:
        TempArrayToList = i.tolist()
        pointsOfPoly.append (TempArrayToList)
    
    min_bounding_box_geom = geometry.Polygon(pointsOfPoly).minimum_rotated_rectangle
    min_bounding_box = min_bounding_box_geom.exterior.coords[:-1]
    #Child: "Dad, what rhymes on orange?" 
    # ... 
    #Dad: "No it doesn't"
    min_bounding_boxAsNP = []
    for i in min_bounding_box:
        min_bounding_boxAsNP.append(np.array([i[0],i[1]]))
    return min_bounding_boxAsNP

def offsetNpPoly(points, offset, outer_ccw = 1):
    oldX = []
    oldY = []
    for i in points:
        point = i.tolist()
        oldX.append(point[0])
        oldY.append(point[1])


    num_points = len(oldX)

    newPoints = []

    for indexpoint in range(num_points):
        prev = (indexpoint + num_points -1 ) % num_points
        next = (indexpoint + 1) % num_points
        vnX =  oldX[next] - oldX[indexpoint]
        vnY =  oldY[next] - oldY[indexpoint]
        vnnX, vnnY = normalizeVec(vnX,vnY)
        nnnX = vnnY
        nnnY = -vnnX
        vpX =  oldX[indexpoint] - oldX[prev]
        vpY =  oldY[indexpoint] - oldY[prev]
        vpnX, vpnY = normalizeVec(vpX,vpY)
        npnX = vpnY * outer_ccw
        npnY = -vpnX * outer_ccw
        bisX = (nnnX + npnX) * outer_ccw
        bisY = (nnnY + npnY) * outer_ccw
        bisnX, bisnY = normalizeVec(bisX,  bisY)
        bislen = offset /  np.sqrt((1 + nnnX*npnX + nnnY*npnY)/2)

        newPoints.append(np.array([oldX[indexpoint] + bislen * bisnX, oldY[indexpoint] + bislen * bisnY]))
    return newPoints

def arrangePolygonPieces(listOfPiecesAsNP, counter = 0):
    loops = []
    for i in listOfPiecesAsNP:
        if len(loops) == 0:
            loops.append(i)
            continue
        appended = False
        for k in loops:
            if np.all(i[0] == k[-1]):
                for f in i:
                    k.append(f)
                    appended = True
            if appended == True:
                break
        if appended == False:
            loops.append(i)
    newLoops = []
    if all(np.all(i[0] == i[-1]) for i in loops) or counter > 5:
        for t in loops:
            singleLoop = []
            for j in t:
                if len(singleLoop) == 0:
                    singleLoop.append(j)
                elif any(np.all(j == x) for x in singleLoop) == False:
                    singleLoop.append(j)
            newLoops.append(singleLoop)
        return newLoops
    else:
        counter =+1
        arrangePolygonPieces(loops, counter)


    distance = np.sqrt(x*x+y*y)
    return x/distance, y/distance

def polygonSplit(unidirectionalPolygonAsNp,cuttingDir_H_or_V,percentageOfCut):   #Input can be whatever way, function works with counterclockwise polygons though! (returns Clockwise)
    
    if determine_loop_direction(unidirectionalPolygonAsNp) == "Clockwise":
        streetToConnectToAsNPVertices = []
        for i in range(len(unidirectionalPolygonAsNp)):      #Make Polygon Counter-clockwise... there was confusion about which direction we work with, too much work to change now, i'm sorry Zuardin (Or anyone else for that matter)
            streetToConnectToAsNPVertices.append(unidirectionalPolygonAsNp[len(unidirectionalPolygonAsNp)-(i+1)])
    else:
        streetToConnectToAsNPVertices = unidirectionalPolygonAsNp.copy()
    bbo = minimalBoundingBox(streetToConnectToAsNPVertices)
    bb = offsetNpPoly(bbo,0.001,1)#Offset Bounding Box ever so slightly larger outwards to prevent intersecting Bug that sometimes happens otherwise (presumeably because of inaccurately rounded numbers)
    sideA = np.linalg.norm(bb[1]-bb[0])
    sideB = np.linalg.norm(bb[1]-bb[2])
    if cuttingDir_H_or_V == "H":   #Cut polygon Horizontaly through minimal bounding box
        if sideA >= sideB:
            dirVec = bb[1]-bb[0]       
            scaledVec = scaleVec(dirVec,np.linalg.norm(dirVec)*(percentageOfCut/100))
            cutLine = [bb[0]+scaledVec,bb[3]+scaledVec]     #Find cutting line fromBoundingbox
        else:
            dirVec = bb[1]-bb[2]       
            scaledVec = scaleVec(dirVec,np.linalg.norm(dirVec)*(percentageOfCut/100))
            cutLine = [bb[3]+scaledVec,bb[2]+scaledVec]     #Find cutting line fromBoundingboxprint("CutLine",cutLine)

    if cuttingDir_H_or_V == "V":    #Cut polygon Vertically through minimal bounding box
        if sideA <= sideB:
            dirVec = bb[1]-bb[0]       
            scaledVec = scaleVec(dirVec,np.linalg.norm(dirVec)*(percentageOfCut/100))
            cutLine = [bb[0]+scaledVec,bb[3]+scaledVec]     #Find cutting line fromBoundingbox
        else:
            dirVec = bb[1]-bb[2]       
            scaledVec = scaleVec(dirVec,np.linalg.norm(dirVec)*(percentageOfCut/100))
            cutLine = [bb[3]+scaledVec,bb[2]+scaledVec]     #Find cutting line fromBoundingboxprint("CutLine",cutLine)

    connectStreetLines = []
    for i in range(len(streetToConnectToAsNPVertices)):   #Convert Polygon to lines
        if i < len(streetToConnectToAsNPVertices)-1:
            CurrentLine = [streetToConnectToAsNPVertices[i], streetToConnectToAsNPVertices[i+1]]
            connectStreetLines.append(CurrentLine)
        else:
            CurrentLine = [streetToConnectToAsNPVertices[i], streetToConnectToAsNPVertices[i-(len(streetToConnectToAsNPVertices)-1)]]
            connectStreetLines.append(CurrentLine)
    for p in streetToConnectToAsNPVertices:       #Test if cutline runs through vertice of polygon which can lead to problems
        if pointOnLineSegment(p, cutLine) == True:
            if np.all(p != cutLine[0]) and np.all(p != cutLine[1]):
                return "no split possible because cutline runs through vertice of polygon"
    
    intersectPoints = []
    listOfVerticesAfterCut = []
    for j in connectStreetLines: #test for intersections between polygon and cutline
        testLines = [j,cutLine]
        if isIntersecting(testLines) == True:
            tempIntersectPoint = getIntersectPoint(testLines)
            if type(tempIntersectPoint) is not np.ndarray:   # if split line is collinear with polygon-line and runs through it: no split happens at this point.
                intersectPoints = []               
                continue
            elif any(np.array_equal(tempIntersectPoint, x) for x in intersectPoints):     #When cut goes through a vertice the cutpoint should not be appended twice
                continue
            else:
                intersectPoints.append(tempIntersectPoint)
                listOfVerticesAfterCut.append(j[1])
                tempIntersectPoint = []
    if (len(intersectPoints) % 2 ) != 0:    #Remove? Evaluate wether needed!
        return "no split possible due to odd intersection number" 

    allPtsForNewPolys = []
    for i in streetToConnectToAsNPVertices:               #Copying polygonasnp into new list, somehow didnt work with "copy()"
        allPtsForNewPolys.append(i)

    for k in range(len(intersectPoints)):               #Insert cutpoints into their correct place in list of polygon-vertices
        if np.all(intersectPoints[k] == listOfVerticesAfterCut[k]):
            continue                                   
        ind = arrayIndex(allPtsForNewPolys,listOfVerticesAfterCut[k])
        allPtsForNewPolys.insert(ind, intersectPoints[k])
    intersectInds = []
    for i in intersectPoints:      #Find all indexes of all the intersectionpoints inside the list of all indexes of the entire polygon
        intersectInds.append(arrayIndex(allPtsForNewPolys,i))
    intersectInds.sort()
    longIntersectInds = intersectInds.copy()
    longAllPtsForNewPolys = allPtsForNewPolys.copy()
    
    for j in range(2):
        for i in intersectInds:     #Append the entire intersectInds list to itself again to basically loop list
            longIntersectInds.append(i)
        for i in allPtsForNewPolys:     #Append the entire allPtsForNewPoly list to itself again to basically loop list
            longAllPtsForNewPolys.append(i)
    
    if len(intersectPoints) > 2:            #If the polygon has multiple cutting-points, search for cutting-point connection that basically "Jumps back" over other points
        intersectLines = []
        for i in range(len(intersectPoints)):   #Convert Polygon to lines
            if i < len(intersectPoints)-1:
                CurrentLine = [intersectPoints[i], intersectPoints[i+1]]
                intersectLines.append(CurrentLine)
            else:
                CurrentLine = [intersectPoints[i], intersectPoints[i-(len(intersectPoints)-1)]]
                intersectLines.append(CurrentLine)
        intersectLineLengths = []
        for i in intersectLines:
            intersectLineLengths.append(np.linalg.norm(i[1]-i[0]))
        maxInd = intersectLineLengths.index(max(intersectLineLengths))
        forbiddenLine = [[intersectLines[maxInd][0].round(5),intersectLines[maxInd][1].round(5)],[intersectLines[maxInd][1].round(5),intersectLines[maxInd][0].round(5)]]
    
    elif len(intersectPoints) <= 2:     #If the polygon has multiple cutting-points, search for cutting-point connection that basically "Jumps back" over other points
        intersectLines = [[intersectPoints[0].round(5),intersectPoints[1].round(5)],[intersectPoints[1].round(5),intersectPoints[0].round(5)]]
        lengthFromIntersectStart = []
        for i in intersectLines:
            lengthFromIntersectStart.append(np.linalg.norm(i[0]-cutLine[0]))
        if lengthFromIntersectStart[0] <= lengthFromIntersectStart[1]:
            forbiddenLineLeft = [intersectLines[0],intersectLines[0]]
            forbiddenLineRight = [intersectLines[1],intersectLines[1]]
        else:
            forbiddenLineLeft = [intersectLines[1],intersectLines[1]]
            forbiddenLineRight = [intersectLines[0],intersectLines[0]]


    leftLoops = []
    leftLoopParts = []
    rightLoops = []
    rightLoopParts = []

    for i in range(len(intersectInds)):         #Find Loops on left side of Cutline
        firstTP = longAllPtsForNewPolys[longIntersectInds[i]]
        secondTP = longAllPtsForNewPolys[longIntersectInds[i+1]]
        if len(intersectPoints) > 2:    #Make sure that loopfinder doesnt try to jump back over all other loops
            if (all(np.array_equal([firstTP.round(5),secondTP.round(5)][o], forbiddenLine[0][o]) for o in range(len(forbiddenLine[0]))) or 
            all(np.array_equal([secondTP.round(5),firstTP.round(5)][o], forbiddenLine[0][o]) for o in range(len(forbiddenLine[0])))):
                continue
        elif len(intersectPoints) == 2:
            if all(np.array_equal([firstTP.round(5),secondTP.round(5)][o], forbiddenLineLeft[0][o]) for o in range(len(forbiddenLineLeft[0]))):
                continue

        testLoop = [firstTP,secondTP,longAllPtsForNewPolys[longIntersectInds[i+1]+1]]
        currentLoop = []
        if determine_loop_direction(testLoop) == "Counterclockwise":
            currentLoop = [firstTP,secondTP]
            for j in range(len(allPtsForNewPolys)):
                currentLoop.append(longAllPtsForNewPolys[longIntersectInds[i+1]+1+j])
                if any(np.array_equal(longAllPtsForNewPolys[longIntersectInds[i+1]+1+j], x) for x in intersectPoints):
                    break                    
                
                    
        else:
            continue
        
        if np.all(currentLoop[-1] == currentLoop[0]):
            del currentLoop[-1]
            leftLoops.append(currentLoop)
        else:
            leftLoopParts.append(currentLoop)
        
    for i in reversed(range(len(intersectInds))):         #Find Loops on right side of Cutline
        firstTP = longAllPtsForNewPolys[longIntersectInds[i]]
        secondTP = longAllPtsForNewPolys[longIntersectInds[i-1]]

        if len(intersectPoints) > 2:    #Make sure that loopfinder doesnt try to jump back over all other loops
            if (all(np.array_equal([firstTP.round(5),secondTP.round(5)][o], forbiddenLine[0][o]) for o in range(len(forbiddenLine[0]))) or 
            all(np.array_equal([secondTP.round(5),firstTP.round(5)][o], forbiddenLine[0][o]) for o in range(len(forbiddenLine[0])))):
                continue
        elif len(intersectPoints) == 2:
            if all(np.array_equal([firstTP.round(5),secondTP.round(5)][o], forbiddenLineRight[0][o]) for o in range(len(forbiddenLineRight[0]))):
                continue

        testLoop = [firstTP,secondTP,longAllPtsForNewPolys[longIntersectInds[i-1]+1]]
        currentLoop = []
        if determine_loop_direction(testLoop) == "Counterclockwise":
            currentLoop = [firstTP,secondTP]
            for j in range(len(allPtsForNewPolys)):
                currentLoop.append(longAllPtsForNewPolys[longIntersectInds[i-1]+1+j])
                if any(np.array_equal(longAllPtsForNewPolys[longIntersectInds[i-1]+1+j], x) for x in intersectPoints):
                    break                    
                
                    
        else:
            continue
        if np.all(currentLoop[-1] == currentLoop[0]):
            del currentLoop[-1]
            rightLoops.append(currentLoop)
        else:
            rightLoopParts.append(currentLoop)

   
    if len(rightLoopParts) >= 2:
        currentRightLoops = arrangePolygonPieces(rightLoopParts)
        for i in currentRightLoops:
            rightLoops.append(i)

    if len(leftLoopParts) >= 2:
        currentLeftLoops = arrangePolygonPieces(leftLoopParts)
        for i in currentLeftLoops:
            leftLoops.append(i)
            
    turnedLeftLoops = []
    turnedRightLoops = []
    for b in leftLoops:
        tempTurn = []
        for i in range(len(b)):      
            tempTurn.append(b[len(b)-(i+1)])
        turnedLeftLoops.append(tempTurn)
    for b in rightLoops:
        tempTurn = []
        for i in range(len(b)):     
            tempTurn.append(b[len(b)-(i+1)])
        turnedRightLoops.append(tempTurn)
    return [turnedLeftLoops,turnedRightLoops]

def pointInPoly(pointAsNP,polyAsNPLines):
    pointList = pointAsNP.tolist()
    polyNP = []
    poly = []

    for i in polyAsNPLines:
        polyNP.append(i[0])
    for i in polyNP:
        poly.append(i.tolist())

    if len(poly) < 3:  # not a polygon - no areaNp
        return False
    
    total = 0
    i = 0
    x = pointList[0]
    y = pointList[1]
    next = 0
    for i in range(len(poly)):
        next = (i + 1) % len(poly)
        if poly[i][1] <= y < poly[next][1]:
            if x < poly[i][0] + (y - poly[i][1]) * (poly[next][0] - poly[i][0]) / (poly[next][1] - poly[i][1]):
                total += 1
        elif poly[next][1] <= y < poly[i][1]:
            if x < poly[i][0] + (y - poly[i][1]) * (poly[next][0] - poly[i][0]) / (poly[next][1] - poly[i][1]):
                total += 1
    if total % 2 == 0:
        return False
    else:
        return True

def pointOnLine(pointAsNP,lineAsNP):
    # NP to List
    lineList = []
    tempPoint = []
    for i in lineAsNP:
        tempPoint = i.tolist()
        lineList.append (tempPoint)
    pointList = pointAsNP.tolist()
    
    endpoint1 = lineList[0]
    endpoint2 = lineList[1]
    #Exeption for Vertical lines with undefined slope
    if (endpoint2[0] - endpoint1[0]) == 0:
        if pointList[0] == endpoint1[0]:
            #Point Is On Line
            return True
        else:
            #Point is not on line
            return False
    #Calculate Slope
    else:
        slope = (endpoint2[1] - endpoint1[1]) / (endpoint2[0] - endpoint1[0])

    # Calculate the y-intercept of the line segment
    y_intercept = endpoint1[1] - (slope * endpoint1[0])
    # Calculate the y-coordinate of the point on the line segment
    y_on_line = (slope * pointList[0]) + y_intercept

    # Check if the y-coordinate of the point is equal to the y-coordinate of the point passed to the function
    if y_on_line == pointList[1]:
        #Point is on line
        return True
    else:
        #Point is not on line
        return False

def pointOnLineSegment(pointAsNP, lineAsNP, threshold = 1e-3):
    p, q, r = lineAsNP[0], pointAsNP, lineAsNP[1]
    if (q[0] <= max(p[0], r[0]) + threshold and q[0] >= min(p[0], r[0]) - threshold and
        q[1] <= max(p[1], r[1]) + threshold and q[1] >= min(p[1], r[1]) - threshold and
        abs(np.cross(r - p, q - p)) < threshold):
        return True
    else:
        return False

def isIntersecting(intersectLinesAsNPList):
    class Point:
        def __init__(self, x, y):
            self.x = x
            self.y = y


    # Given three collinear points p, q, r, the function checks if
    # point q lies on line segment 'pr'
    def onSegment(p, q, r):
        if ( (q.x <= max(p.x, r.x)) and (q.x >= min(p.x, r.x)) and
            (q.y <= max(p.y, r.y)) and (q.y >= min(p.y, r.y))):
            return True
        return False

    def orientation(p, q, r):
    #Find point orientation
        val = (float(q.y - p.y) * (r.x - q.x)) - (float(q.x - p.x) * (r.y - q.y))
        if (val > 0):
            
            # Clockwise orientation
            return 1
        elif (val < 0):
            
            # Counterclockwise orientation
            return 2
        else:
            
            # Collinear orientation
            return 0

    # The main function that returns true if
    # the line segment 'p1q1' and 'p2q2' intersect.
    def doIntersect(p1,q1,p2,q2):
        
        # Find the 4 orientations required for
        # the general and special cases
        o1 = orientation(p1, q1, p2)
        o2 = orientation(p1, q1, q2)
        o3 = orientation(p2, q2, p1)
        o4 = orientation(p2, q2, q1)

        # General case
        if ((o1 != o2) and (o3 != o4)):
            return True

        # Special Cases

        # p1 , q1 and p2 are collinear and p2 lies on segment p1q1
        if ((o1 == 0) and onSegment(p1, p2, q1)):
            return True

        # p1 , q1 and q2 are collinear and q2 lies on segment p1q1
        if ((o2 == 0) and onSegment(p1, q2, q1)):
            return True

        # p2 , q2 and p1 are collinear and p1 lies on segment p2q2
        if ((o3 == 0) and onSegment(p2, p1, q2)):
            return True

        # p2 , q2 and q1 are collinear and q1 lies on segment p2q2
        if ((o4 == 0) and onSegment(p2, q1, q2)):
            return True

        # If none of the cases
        return False

    TempArrayToList = []
    tempArray1 = []
    for i in intersectLinesAsNPList:
        for j in i:
            tempArray1.append(j.tolist())
        TempArrayToList.append(tempArray1)
        tempArray1 = []

    
    p1 = Point(TempArrayToList[0][0][0],TempArrayToList[0][0][1])
    q1 = Point(TempArrayToList[0][1][0],TempArrayToList[0][1][1])
    p2 = Point(TempArrayToList[1][0][0],TempArrayToList[1][0][1])
    q2 = Point(TempArrayToList[1][1][0],TempArrayToList[1][1][1])
    
    if doIntersect(p1, q1, p2, q2):
        return True
    else:
        return False

def getIntersectPoint(intersectLinesAsNPList):
    
    x1, y1 = intersectLinesAsNPList[0][0]
    x2, y2 = intersectLinesAsNPList[0][1]
    x3, y3 = intersectLinesAsNPList[1][0]
    x4, y4 = intersectLinesAsNPList[1][1]

    if (x1, y1) == (x3, y3) or (x1, y1) == (x4, y4):#Check if Intersection-point is already included in input because x_num and y_num are = 0 otherwise which causes mistakes
        return np.array([x1, y1])
    if (x2, y2) == (x3, y3) or (x2, y2) == (x4, y4):
        return np.array([x2, y2])

    x_num = (x1*y2 - y1*x2) * (x3 - x4) - (x1 - x2) * (x3*y4 - y3*x4)
    y_num = (x1*y2 - y1*x2) * (y3 - y4) - (y1 - y2) * (x3*y4 - y3*x4)
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    
    if denom == 0:
        return "Lines are parallel"
    x = x_num / denom
    y = y_num / denom
    return np.array([x, y])

    """a1 = intersectLinesAsNPList[0][0]
    a2 = intersectLinesAsNPList[0][1]
    b1 = intersectLinesAsNPList[1][0]
    b2 = intersectLinesAsNPList[1][1]
    
    s = np.vstack([a1,a2,b1,b2])        # s for stacked
    h = np.hstack((s, np.ones((4, 1)))) # h for homogeneous
    l1 = np.cross(h[0], h[1])           # get first line
    l2 = np.cross(h[2], h[3])           # get second line
    x, y, z = np.cross(l1, l2)          # point of intersection
    if z == 0:                          # lines are parallel
        return "False"
    return np.array([x/z, y/z])         # returns intersection point as NP-Array"""

def pointOnPolygon(pointAsNP,polygonAsNPLines):
    for i in polygonAsNPLines:
        if pointOnLineSegment(pointAsNP,i) == True:
            return True
    return False

def scaleVec(vecAsNP,newLength):
    distance = np.linalg.norm(vecAsNP)
    scale_factor = newLength / distance
    return vecAsNP * scale_factor

def normalizeNpVec(vec):
    return vec / np.linalg.norm(vec)

def mainStreetGenerator(BaseShape,InputLines): #Edit: Write exception for collinear inputlines! Write exaption for inputline that generates street segment through another inputpoint #Write exception for self-interecting Polygon!!!
    """for i in InputLines:
        for j in InputLines:
            if np.array_equal(i,j):
                continue
            intersect = isIntersecting([i,j])"""
    #Find valid generation starting points
    startPointAndVec = [] 
    generatedStreets = []
    for i in InputLines:
        pc = []
        #Testing both points of the current Inputline for their position
        for j in i:
            if pointOnPolygon(j,BaseShape) == True:
                pc.append("onOutline")
                continue
            elif pointInPoly(j,BaseShape) == True:
                pc.append("inside")
                continue
            else:
                pc.append("outside")
       
        #Generating start-points and vectors for the street generation out of the inputlines and their points' conditions

        if pc[0] == "outside" and pc[1] == "outside": #Both points are outside of baseshape
            intersectPoints = []
            for j in BaseShape: #test if inputline runs through base shape (for every boundary line of base shape) despite endpoints beeing outside
                testLines = [i]
                testLines.append(j)
                if isIntersecting(testLines) == True:
                    tempIntersectPoint = getIntersectPoint(testLines)
                    if type(tempIntersectPoint) is not np.ndarray:   # Exeption if line runs through baseshape but is colinear with boundary line
                        intersectPoints = []               # - of baseshape which could lead to problems
                        break                                  
                    else:
                        intersectPoints.append(tempIntersectPoint)
                        tempIntersectPoint = []
            
            if len(intersectPoints) == 2:                 # if the endpoints of the inputline are outside the baseshape, but it intersects the baseshape twice, 
                generatedStreets.append(intersectPoints)  # - the resulting line inside the baseshape is effectivly a valid street
            else:
                continue
            
        if pc[0] == "inside" and pc[1] == "inside": #Both points are contained in baseshape
            intersectPoints = []
            for j in BaseShape: #test if inputline runs through base shape (for every boundary line of base shape) despite endpoints beeing inside
                testLines = [i]
                testLines.append(j)
                if isIntersecting(testLines) == True:
                    tempIntersectPoint = getIntersectPoint(testLines)
                    if type(tempIntersectPoint) is not np.ndarray:        # Exeption if line runs through baseshape but is colinear with boundary line
                        intersectPoints = []               # - of baseshape which could lead to problems
                        break                                  
                    else:
                        intersectPoints.append(tempIntersectPoint)
                        tempIntersectPoint = []
            if len(intersectPoints) == 0:  #When there are no intersections with the outter lines, midpoint of inputline = start, and vectors in both directions as dir_vecs
                tP = []
                for p in i:
                    tP.append(p.tolist())
                midpoint = np.array([(tP[0][0] + tP[1][0])/2, (tP[0][1] + tP[1][1])/2])
                for p in i:
                    dirVec = p - midpoint
                    dirVecScaled = normalizeNpVec(dirVec)
                    startPointAndVec.append([midpoint,dirVecScaled])
                continue
            elif len(intersectPoints) == 1: #When there is one intersectionpoint with the edges, just take the intersectionpoint as start
                for p in i:
                    dirVec = p - intersectPoints[0]
                    dirVecScaled = normalizeNpVec(dirVec)
                    startPointAndVec.append([intersectPoints[0],dirVecScaled])
                continue
            elif len(intersectPoints) == 2:  #When there are two intersectionpoints with the boundary, take the closest to the point as start and calculate dir_vec
                for p in i:
                    pointDistance = []
                    for k in intersectPoints:
                        pointDistance.append(np.linalg.norm(k-p))
                    if pointDistance[0] < pointDistance[1]:
                        dirVec = p - intersectPoints[0]
                        dirVecScaled = normalizeNpVec(dirVec)
                        startPointAndVec.append([intersectPoints[0],dirVecScaled])
                    elif pointDistance[0] > pointDistance[1]:
                        dirVec = p - intersectPoints[1]
                        dirVecScaled = normalizeNpVec(dirVec)
                        startPointAndVec.append([intersectPoints[1],dirVecScaled])
                    else:
                        continue
            else:
                continue
        
        if pc[0] == "onOutline" and pc[1] == "onOutline": #Both points are on the baseshapes outline DEACTIVATED, MAYBE FIX LATER
            continue #Both points on outline have a high chance to be no ciable street. Could also mean street outside of polygon. MAYBE FIX LATER!
        
        if pc[0] == "inside" and pc[1] == "outside" or pc[0] == "outside" and pc[1] == "inside": #One point inside of baseshape, other outside
            intersectPoints = []
            for j in BaseShape: #test on every boundary line of base shape for intersection and find out intersection point
                testLines = [i]
                testLines.append(j)
                if isIntersecting(testLines) == True:
                    tempIntersectPoint = getIntersectPoint(testLines)
                    if type(tempIntersectPoint) is not np.ndarray:   # Exeption if line runs through baseshape but is colinear with boundary line
                        intersectPoints = []          # - of baseshape which could lead to problems
                        break                                  
                    else:
                        intersectPoints.append(tempIntersectPoint)
                        tempIntersectPoint = []
            if len(intersectPoints) == 1: #If the line has one intersection with baseshape, this is starting point for generation, dir_vec towards point in baseshape
                if pc[0] == "inside":
                    dirVec = i[0] - intersectPoints[0]
                    dirVecScaled = normalizeNpVec(dirVec)
                    startPointAndVec.append([intersectPoints[0],dirVecScaled])
                    continue
                elif pc[1] == "inside":
                    dirVec = i[1] - intersectPoints[0]
                    dirVecScaled = normalizeNpVec(dirVec)
                    startPointAndVec.append([intersectPoints[0],dirVecScaled])
                    continue
                else:
                    continue
            
            elif len(intersectPoints) > 1:   #If the line has multiple intersections,closest intersection to the inside-point is takes as start, inside-point for dir_vec
                if pc[0] == "inside":
                    pointDistance = []
                    for k in intersectPoints:
                        pointDistance.append(np.linalg.norm(k - i[0]))
                    minpos = pointDistance.index(min(pointDistance))
                    dirVec = i[0] - intersectPoints[minpos]
                    dirVecScaled = normalizeNpVec(dirVec)
                    startPointAndVec.append([intersectPoints[minpos],dirVecScaled])
                    continue
                elif pc[1] == "inside":
                    pointDistance = []
                    for k in intersectPoints:
                        pointDistance.append(np.linalg.norm(k - i[1]))
                    minpos = pointDistance.index(min(pointDistance))
                    dirVec = i[1] - intersectPoints[minpos]
                    dirVecScaled = normalizeNpVec(dirVec)
                    startPointAndVec.append([intersectPoints[minpos],dirVecScaled])
                    continue
            else:
                continue

        if pc[0] == "inside" and pc[1] == "onOutline" or pc[0] == "onOutline" and pc[1] == "inside": #One point inside baseshape, other on it's outline
            intersectPoints = []
            for j in BaseShape: #test on every boundary line of base shape for intersection and find out intersection point
                testLines = [i]
                testLines.append(j)
                if isIntersecting(testLines) == True:
                    tempIntersectPoint = getIntersectPoint(testLines)
                    if type(tempIntersectPoint) is not np.ndarray:   # Exeption if line runs through baseshape but is colinear with boundary line
                        intersectPoints = []          # - of baseshape which could lead to problems
                        break                                  
                    else:
                        intersectPoints.append(tempIntersectPoint)
                        tempIntersectPoint = []
            if len(intersectPoints) == 1:  #If the line has one intersection (should be the point which is on the line) take this as start, iside point as dir_vec
                if pc[0] == "inside":
                    dirVec = i[0] - intersectPoints[0]
                    dirVecScaled = normalizeNpVec(dirVec)
                    startPointAndVec.append([intersectPoints[0],dirVecScaled])
                    continue
                elif pc[1] == "inside":
                    dirVec = i[1] - intersectPoints[0]
                    dirVecScaled = normalizeNpVec(dirVec)
                    startPointAndVec.append([intersectPoints[0],dirVecScaled])
                    continue
                else:
                    continue
            elif len(intersectPoints) > 1:   #If the line has multiple intersections,closest intersection to the inside-point is takes as start, inside-point for dir_vec
                if pc[0] == "inside":
                    pointDistance = []
                    for k in intersectPoints:
                        pointDistance.append(np.linalg.norm(k - i[0]))
                    minpos = pointDistance.index(min(pointDistance))
                    dirVec = i[0] - intersectPoints[minpos]
                    dirVecScaled = normalizeNpVec(dirVec)
                    startPointAndVec.append([intersectPoints[minpos],dirVecScaled])
                    continue
                elif pc[1] == "inside":
                    pointDistance = []
                    for k in intersectPoints:
                        pointDistance.append(np.linalg.norm(k - i[1]))
                    minpos = pointDistance.index(min(pointDistance))
                    dirVec = i[1] - intersectPoints[minpos]
                    dirVecScaled = normalizeNpVec(dirVec)
                    startPointAndVec.append([intersectPoints[minpos],dirVecScaled])
                    continue
            else:
                continue

        if pc[0] == "onOutline" and pc[1] == "outside" or pc[0] == "outside" and pc[1] == "onOutline": #One point on Outline, other outside DEACTIVATED, MAYBE FIX LATER
            continue

        else:
            continue
        
    for i in startPointAndVec:

        def generateStreetSegment(startPoint,dirVec,BaseShape,existingStreets,segmentLength):
            
            newDirVec = scaleVec(dirVec,segmentLength)
            currentSegment = [startPoint, startPoint + newDirVec]
            intersectPoints = []
            allLinesToTest = BaseShape + existingStreets
            
            for j in allLinesToTest: #test on every boundary line of base shape for intersection and find out intersection points
                testLines = [currentSegment]
                testLines.append(j)
                if isIntersecting(testLines) == True:
                    tempIntersectPoint = getIntersectPoint(testLines)
                    if type(tempIntersectPoint) is not np.ndarray:   # Exeption if line runs through baseshape but is colinear with boundary line
                        intersectPoints = []          # - of baseshape which could lead to problems
                        break                                  
                    else:
                        intersectPoints.append(tempIntersectPoint)
                        tempIntersectPoint = []

            spList = startPoint.tolist()
            spListRounded = []
            for i in spList:
                spListRounded.append(round(i,3))
            ipList = []
            for b in intersectPoints:
                ipList.append(b.tolist())
            
            ipListRounded = []
            tempIpList = []
            for o in ipList:
                for k in o:
                    tempIpList.append(round(k,3))
                ipListRounded.append(tempIpList)
                tempIpList = []
  
            if spListRounded in ipListRounded:
                ind = ipListRounded.index(spListRounded)
                del intersectPoints[ind]

            if len(intersectPoints) == 0:
                return "noIntersect"
            elif len(intersectPoints) == 1:
                return [startPoint,intersectPoints[0]]
            elif len(intersectPoints) > 1:
                pointDistance = []
                for k in intersectPoints:
                    pointDistance.append(np.linalg.norm(k - startPoint))
                minpos = pointDistance.index(min(pointDistance))
                return [startPoint,intersectPoints[minpos]]
            


        def system(startPoint,dirVec,BaseShape,existingStreets,segmentLength):
            
            segmentLength += 500 
            currentStreetSegment = generateStreetSegment(startPoint,dirVec,BaseShape,existingStreets,segmentLength)
            if currentStreetSegment == "noIntersect" and segmentLength <= 500:
                return system(startPoint,dirVec,BaseShape,existingStreets,segmentLength)
            elif currentStreetSegment == "noIntersect" and segmentLength > 500:
                return "false"
            else:
                return currentStreetSegment

        segmentLength = 0
        
        currentGeneratedStreet = system(i[0],i[1],BaseShape,generatedStreets,segmentLength)
        if currentGeneratedStreet == "false":
            continue
        else:
            generatedStreets.append(currentGeneratedStreet)

    return generatedStreets

def splitLine(lineToSplitAsNP,splittingLineOrPointAsNP):
    if len (lineToSplitAsNP) == 2:
        if type(splittingLineOrPointAsNP) is np.ndarray and len(splittingLineOrPointAsNP) == 2:
            if (splittingLineOrPointAsNP == lineToSplitAsNP[0]).all() or (splittingLineOrPointAsNP == lineToSplitAsNP[1]).all():
                return "Intersecting only in Endpoint of Line"
            isOnLine = pointOnLineSegment(splittingLineOrPointAsNP,lineToSplitAsNP)
            if isOnLine == False:
                return "notIntersecting"
            else:
                return [[lineToSplitAsNP[0],splittingLineOrPointAsNP],[splittingLineOrPointAsNP,lineToSplitAsNP[1]]]

        elif type(splittingLineOrPointAsNP) is list and len(splittingLineOrPointAsNP) == 2:
            for i in lineToSplitAsNP:
                if pointOnLineSegment(i,splittingLineOrPointAsNP) == True:
                    return "Intersecting only in Endpoint of Line to split or Lines are identical"
            if isIntersecting([lineToSplitAsNP,splittingLineOrPointAsNP]) == True:
                intersectPoint = getIntersectPoint([lineToSplitAsNP,splittingLineOrPointAsNP])
                if type(intersectPoint) is not np.ndarray:
                    return "no single splittingpoint"
                else:
                    return [[lineToSplitAsNP[0],intersectPoint],[intersectPoint,lineToSplitAsNP[1]]]
            else:
                return "notIntersecting"
        else:
            return "please only pass a single point or line as splittingLineOrPointAsNP"
    else:
        return "please only provide a single line to split"

def splitMultipleLines(linesToSplitAsNP):
    splitLines = []
    for i in linesToSplitAsNP:
        intersectPoints = []
        for j in linesToSplitAsNP:
            if np.array_equal(i,j):
                continue
            if isIntersecting([i,j]) == True or pointOnLineSegment(j[0],i) or pointOnLineSegment(j[1],i):
                if np.array_equal(i[0],j[0]) or np.array_equal(i[0],j[1]) or np.array_equal(i[1],j[0]) or np.array_equal(i[1],j[1]):
                    continue
                if pointOnLineSegment(i[0],j) or pointOnLineSegment(i[1],j):
                    continue
                else:
                    
                    currentIntersect = getIntersectPoint([i,j])
                    
                    if type(currentIntersect) is not np.ndarray:
                        continue
                    intersectPoints.append(currentIntersect)
            else:
                continue

        if len(intersectPoints) == 1:
            splitLines.append([i[0],intersectPoints[0]])
            splitLines.append([intersectPoints[0],i[1]])
            continue
        else:
            start = i[0]
            end = i[1]
            # Get the vector of the line segment
            lineVec = end - start
            # Create a list to store the ordered points
            orderedPoints = []
            for point in intersectPoints:
                # Get the vector from the start of the line segment to the point
                pointVec = point - start
                # Use the dot product to determine the position of the point on the line segment
                position = np.dot(pointVec, lineVec)
                # Append the point and its position to the list
                orderedPoints.append((point, position))
            # Sort the list of points based on their position on the line segment
            orderedPoints.sort(key=lambda x: x[1])
            # Return only the points
            pointsInOrder = [point for point, position in orderedPoints]
            pointsInOrder.insert(0, i[0])
            pointsInOrder.append(i[1])
            for k in range(len(pointsInOrder)-1):
                splitLines.append([pointsInOrder[k],pointsInOrder[k+1]])
    return splitLines


##########################################################################################
lines=[
[[0, 0],[ 2, 2]],#Input Lines
[[2, 2], [2, 0]], 
[[2, 0], [0, 0]],
[[6, 0], [4, 1]], 
[[4, 1], [2, 0]], 
[[2, 0], [2, 2]],
[[2, 2], [6, 2]], 
[[6, 2], [6, 0]], 
[[6, 0], [6, 2]], 
[[6, 2], [8, 3]], 
[[8, 3], [9, 1]], 
[[9, 1], [8, 0]], 
[[8, 0], [6, 0]], 
[[6, 4], [6, 5]], 
[[6, 5], [8, 5]], 
[[8, 5], [8, 3]], 
[[8, 3], [6, 2]], 
[[6, 2], [6, 4]], 
[[6, 4], [3, 4]], 
[[3, 4], [2, 2]], 
[[2, 2], [6, 2]], 
[[6, 2], [6, 4]], 
[[0, 0], [0, 3]], 
[[0, 3], [2, 2]], 
[[2, 2], [0, 0]], 
[[0, 3], [2, 2]], 
[[2, 2], [3, 4]], 
[[3, 4], [3, 5]], 
[[3, 5], [0, 5]], 
[[0, 5], [0, 3]], 
[[6, 4], [6, 5]], 
[[6, 5], [3, 5]], 
[[3, 5], [3, 4]], 
[[3, 4], [6, 4]], 
[[6, 5], [3, 5]], 
[[3, 5], [3, 7]], 
[[3, 7], [6, 5]], 
[[0, 7], [0, 5]], 
[[0, 5], [3, 5]], 
[[3, 5], [3, 7]], 
[[3, 7], [0, 7]]
]

# lines = [
# [[70.5, 100.0], [67.38502673796792, 50.160427807486634]], 
# [[67.38502673796792, 50.160427807486634], [64.25, 0.0]], 
# [[37.5, 69.5], [0.0, 77.0]], 
# [[37.5, 69.5], [68.20987654320987, 63.35802469135801]], 
# [[0.0, 22.083333333333332], [50.0, 42.91666666666667]], 
# [[50.0, 42.91666666666667], [67.38502673796792, 50.16042780748664]], 
# [[50.0, 0.0], [50.0, 42.91666666666668]], 
# [[0, 0], [0.0, 22.083333333333332]], 
# [[0.0, 22.083333333333332], [0.0, 77.0]], 
# [[0.0, 77.0], [0, 100]], 
# [[0, 100], [70.5, 100.0]], 
# [[70.5, 100.0], [100, 100]], 
# [[100, 100], [100, 0]], 
# [[100, 0], [64.25, 0.0]], 
# [[64.25, 0.0], [50.0, 0.0]], 
# [[50.0, 0.0], [0, 0]]
# ]



# Simple render and animate

def render(*args):
    global linesIfinal, meshesIfinal,scene
    window.requestAnimationFrame(create_proxy(render))
    updateI()
    updateO ()
    updateL ()
    
  
    controls.update()
    
    composer.render()
    #updatePlotassignerAndScene ()
    

   
    


    #update (args[0], args[1], args[2])
    #print("auf")

# Graphical post-processing



def post_process():

    render_pass = THREE.RenderPass.new(scene, camera)
    render_pass.clearColor = THREE.Color.new(0,0,0)
    render_pass.ClearAlpha = 0
    fxaa_pass = THREE.ShaderPass.new(THREE.FXAAShader)
    pixelRatio = window.devicePixelRatio
    fxaa_pass.material.uniforms.resolution.value.x = 1 / ( window.innerWidth * pixelRatio )
    fxaa_pass.material.uniforms.resolution.value.y = 1 / ( window.innerHeight * pixelRatio )

    global composer
    composer = THREE.EffectComposer.new(renderer)
    composer.addPass(render_pass)
    composer.addPass(fxaa_pass)

# Adjust display when window size changes

def on_window_resize(event):
    event.preventDefault()
    global renderer
    global camera
    camera.aspect = window.innerWidth / window.innerHeight
    camera.updateProjectionMatrix()
    renderer.setSize( window.innerWidth, window.innerHeight )

    #postprocessing after resize
    post_process()

#-----------------------------------------------------------------------

#RUN THE MAIN PROGRAM

if __name__=='__main__':
    main()