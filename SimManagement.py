#from eppy import modeleditor
from eppy.modeleditor import IDF
import os
import copy
import shutil



def gen_idf_run_sim(Sim_dir,building_type,window_orientation,epwfile):
    #__________________________________________________________________________________
    #Set Simulation Directory

    weather_Folder="Weather"
    if os.path.exists(Sim_dir):
        shutil.rmtree(Sim_dir)

    os.makedirs(Sim_dir)

    #__________________________________________________________________________________
    #Template Selection

    #Select proper Template Office or Residential (Source for Gains SIA Merkblatt 2024)
    if building_type == "residential":
        fname1 = "Residential_totalBaseline.idf"
        #drop file extension
        basecase_pre=fname1.split(".")[0]
    elif building_type == "office":
        fname1 = "Office_totalBaseline.idf"
        basecase_pre=fname1.split(".")[0]

    iddfile="C:\EnergyPlusV22-2-0\Energy+.idd"
    IDF.setiddname(iddfile)
    idf1 = IDF(fname1, epwfile)


    #Change the Orientation of the building
    building = idf1.idfobjects['BUILDING'][0]

    if window_orientation == "South":
        building.North_Axis = 0.0 #in template window is on south facade and 0.0 is the default
    elif window_orientation == "East":
        building.North_Axis = 270.0
    elif window_orientation == "West":
        building.North_Axis = 90.0
    elif window_orientation == "North":
        building.North_Axis = 180.0


    # - Save it to the disk
    main_dir=os.path.dirname(os.path.realpath(__file__)) #get path of the file to chnage dir back later
    idf1.idfname = fname1
    idf1.saveas(os.path.join(Sim_dir,fname1)) #save as base

    #Shading start
    #__________________________________________________________________________________
    idf_shading=copy.deepcopy(idf1) #make a deep copy
    #Add Shading
    shading = idf_shading.idfobjects['WindowShadingControl'][0]
    shading.Setpoint = 20.0 #setpoint for shading control

    shading_pre=building_type+"_Shading"
    fname_shading=shading_pre+".idf"
    idf_shading.idfname = fname_shading
    idf_shading.saveas(os.path.join(Sim_dir,fname_shading))
    #__________________________________________________________________________________

    #Ventilation Day Start
    #__________________________________________________________________________________
    idf_ventday=copy.deepcopy(idf_shading) #make a deep copy

    ventilation=idf_ventday.idfobjects['ZoneVentilation:WindandStackOpenArea'][0]
    ventilation.Opening_Area_Fraction_Schedule_Name="NatVentAvail_Zone_0" #only avail between 7 am and 6pm
    ventilation.Opening_Area=3 #3m2
    ventilation.Minimum_Indoor_Temperature=22 #22deg C

    ventday_pre=building_type+"_DayVent"
    fname_ventday=ventday_pre+".idf"
    idf_ventday.idfname = fname_ventday
    idf_ventday.saveas(os.path.join(Sim_dir,fname_ventday))

    #Ventilation Day/Night Start
    #__________________________________________________________________________________
    idf_ventall=copy.deepcopy(idf_ventday) #make a deep copy

    ventilation=idf_ventall.idfobjects['ZoneVentilation:WindandStackOpenArea'][0]
    ventilation.Opening_Area_Fraction_Schedule_Name="AllOn" #always available (at night too)

    ventall_pre=building_type+"_AllVent"
    fname_ventall=ventall_pre+"idf"
    idf_ventall.idfname = fname_ventall
    idf_ventall.saveas(os.path.join(Sim_dir,fname_ventall))

    #Thermal Mass Start
    #__________________________________________________________________________________
    idf_thermalmass=copy.deepcopy(idf_ventall) #make a deep copy
    detailed_surfaces= idf_thermalmass.idfobjects['BuildingSurface:Detailed']

    #set wall material
    walls=[sf for sf in detailed_surfaces if sf.Surface_Type=='Wall']
    for wall in walls:
        wall.Construction_Name = "UVal_0.2_Mass" # make sure such a construction exists in the model

    roofs=[sf for sf in detailed_surfaces if sf.Surface_Type=='Roof']
    for roof in roofs:
        roof.Construction_Name = "UVal_0.2_Mass" # make sure such a construction exists in the model

    floors=[sf for sf in detailed_surfaces if sf.Surface_Type=='Floor']
    for floor in floors:
        floor.Construction_Name = "Slab_Mass_FLIPPED" # make sure such a construction exists in the model

    ventall_mass_pre=building_type+"_AllVent_mass"
    fname_thmass=ventall_mass_pre+".idf"
    idf_thermalmass.idfname = fname_thmass
    idf_thermalmass.saveas(os.path.join(Sim_dir,fname_thmass))


    #Run the Simulations
    #__________________________________________________________________________________
    #this can be paralellized later
    #needs to be faster

    os.chdir(Sim_dir) #Change directory intor directory dedicated to simulation
    idf1.idfname = fname1
    idf1.run(readvars=True,output_prefix=basecase_pre)
    idf_shading.idfname = fname_shading
    idf_shading.run(readvars=True,output_prefix=shading_pre)
    idf_ventday.idfname = fname_ventday
    idf_ventday.run(readvars=True,output_prefix=ventday_pre)
    idf_ventall.idfname = fname_ventall
    idf_ventall.run(readvars=True,output_prefix=ventall_pre)
    idf_thermalmass.idfname = fname_thmass
    idf_thermalmass.run(readvars=True,output_prefix=ventall_mass_pre)
    os.chdir(main_dir) #Change directory intor directory dedicated to simulation

    csv_prefixes = [basecase_pre, shading_pre, ventday_pre, ventall_pre, ventall_mass_pre]

    
    return csv_prefixes
    

'''
#dummy variables from interface
building_type = "Office"
window_orientation = "North"
epwfile= "C:\\Users\\svenj\\OneDrive - Massachusetts Institute of Technology\\00_MIT\\23_Fall\\1125_ArchandEngSoftwareSys\\Project_final\\Version1\\Weather\\USA_NM_Santa.Fe.County.Muni.AP.723656_TMY3.epw"



csv_prefixes=gen_idf_run_sim(building_type,window_orientation,epwfile)
'''