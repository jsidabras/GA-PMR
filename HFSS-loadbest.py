# ----------------------------------------------
# Script Written by Jason W. Sidabras (jason.sidabras@cec.mpg.de)
# requires jsidabras/hycohanz as of 20-04-2017
# Loads a file with a list of 1s and 0s and implements it to HFSS as Silv/Vac
# used to load the best results per generation or final 
# ----------------------------------------------
from random import *
import argparse
import hycohanz as hfss
from datetime import datetime
startTime = datetime.now()

[oAnsoftApp, oDesktop] = hfss.setup_interface()
oProject = hfss.get_active_project(oDesktop)
oDesign = hfss.set_active_design(oProject, 'HFSSDesign1')
oEditor = hfss.set_active_editor(oDesign)
oFieldsReporter = hfss.get_module(oDesign, 'FieldsReporter')

parser = argparse.ArgumentParser(description='Load GA best file and run solution in HFSS.')
parser.add_argument('file', type=str, help='the filename to load')
args = parser.parse_args()

f = open(args.file, 'r')
thing = f.readline()
f.close()

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
   hfss.assign_material(oEditor, Silv, MaterialName="silver", SolveInside=False)

# oProject.Save()
try:
    oDesign.Analyze("Setup1")
except:
    print("Simulation Error Set Fitness to 0")
    # return 0,

oFieldsReporter.CalcStack('clear')
hfss.enter_qty(oFieldsReporter, 'H')
hfss.enter_qty(oFieldsReporter, 'H')
hfss.calc_op(oFieldsReporter, 'Conj')
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
