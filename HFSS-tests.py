# ----------------------------------------------
# Script Written by Jason W. Sidabras (jason.sidabras@cec.mpg.de)
# requires jsidabras/hycohanz as of 20-04-2017
# 20-04-2017: script runs 3m00s for 2490 element change. Hfss-Region 
# (Model/NonModel change) Vacuum can produce non-solvable geometries. Meshed 1 pass
# 20-04-2017: script runs 3m12s for 2490 element change. Removed hfss-Region 
# and replaced with a static subtracted vacuum volume (Model/NonModel change).
# 19-04-2017: script runs 4m44s for 2490 element change (material change). 
# ----------------------------------------------
from random import *
import hycohanz as hfss
from datetime import datetime
startTime = datetime.now()

[oAnsoftApp, oDesktop] = hfss.setup_interface()
oProject = hfss.get_active_project(oDesktop)
oDesign = hfss.set_active_design(oProject, 'HFSSDesign1')
oEditor = hfss.set_active_editor(oDesign)
oFieldsReporter = hfss.get_module(oDesign, 'FieldsReporter')
oSolution = oDesign.GetModule("Solutions")

oDesktop.EnableAutoSave(False)

randBinList = lambda n: [randint(0,1) for b in range(1,n+1)]

thing = randBinList(1721)
print(thing)
index = 0
Vac = []
Silv = []
for i in thing:
    if i == 1:
        Silv.append("Elm_"+str(index))
        index += 1
    else:
        Vac.append("Elm_"+str(index))
        index += 1

oDesktop.ClearMessages("", "", 3)

if Vac: 
# Check if list is empty
    # hfss.assign_White(oEditor, Silv)
    
    hfss.assign_material(oEditor, Vac, MaterialName="vacuum", SolveInside=True)
if Silv:
    # hfss.assign_Orange(oEditor, Silv)
   hfss.assign_material(oEditor, Silv, MaterialName="pec", SolveInside=False)

# oProject.Save()

oEditor.PurgeHistory(["NAME:Selections", "Selections:=", Silv, "NewPartsModelFlag:=", "Model"])
oEditor.PurgeHistory(["NAME:Selections", "Selections:=", Vac, "NewPartsModelFlag:=", "Model"])


try:
    oDesign.Analyze("Setup1")
    
except:
    print("Simulation Error Set Fitness to 0")
    # return 0,
    
oFieldsReporter.CalcStack('clear')
# Load the pre solved calculator expressions. Some will delete when Fastlist is deleted
# Remember to set Ple to zero unless you are solving for the losses in the substrate
#oFieldsReporter.LoadNamedExpressions("E:\\MPI\\Maxwell\\Projects\\PersonalLib\\_Signal_14 - Xband - ICE.clc", "Fields", ["ImDieHold", "ImDieSam", "Frq", "H1r", "H1rMax", "IntH1r2dVs"])
oFieldsReporter.CopyNamedExprToStack("IntH1r2dVs")
# Is there a solution present? If so clc_eval if not, run the Analyze again
# if there is still no solution, send it to zero
if oSolution.HasFields("Setup1:LastAdaptive", "x_size=2mm") == 1:
    hfss.clc_eval(
        oFieldsReporter,
        'Setup1',
        'LastAdaptive',
        9.7e9,
        0,
        {},
    )
else:
    oDesign.Analyze("Setup1")
    hfss.clc_eval(
        oFieldsReporter,
        'Setup1',
        'LastAdaptive',
        9.7e9,
        0,
        {},
    )    
out = hfss.get_top_entry_value(
    oFieldsReporter,
    'Setup1',
    'LastAdaptive',
    9.7e9,
    0,
    {},
)
print(out[0])
print(datetime.now() - startTime)
