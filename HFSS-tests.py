# ----------------------------------------------
# Script Recorded by ANSYS Electronics Desktop Version 2017.0.0
# 13:58:19  Apr 18, 2017
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

thing = randBinList(30)
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

hfss.assign_IsModel(oEditor, Silv, MaterialName="silver", SolveInside=False, IsModel=True)
hfss.assign_IsModel(oEditor, Vac, MaterialName="silver", SolveInside=False, IsModel=False)

oProject.Save()
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
