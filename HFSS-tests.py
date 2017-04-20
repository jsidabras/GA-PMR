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


randBinList = lambda n: [randint(0,1) for b in range(1,n+1)]

thing = randBinList(2490)
index = 0
Vac = []
Silv = []
for i in thing:
    if i == 1:
        Silv.append("Planar_"+str(index))
        index += 1
    else:
        Vac.append("Planar_"+str(index))
        index += 1

oDesktop.ClearMessages("", "", 3)

        
if Vac: 
# Check if list is empty
    # hfss.assign_White(oEditor, Silv)
    hfss.assign_material(oEditor, Vac, MaterialName="vacuum", SolveInside=True)
if Silv:
    # hfss.assign_Orange(oEditor, Silv)
   hfss.assign_material(oEditor, Silv, MaterialName="silver", SolveInside=False)


# oProject.Save()
oDesign.Analyze("Setup1")
hfss.enter_qty(oFieldsReporter, 'H')
hfss.enter_qty(oFieldsReporter, 'H')
hfss.calc_op(oFieldsReporter, 'Dot')
hfss.calc_op(oFieldsReporter, 'Real')
hfss.enter_vol(oFieldsReporter, 'Sample')
hfss.calc_op(oFieldsReporter, 'Integrate')
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
