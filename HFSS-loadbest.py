# ----------------------------------------------
# Script Written by Jason W. Sidabras (jason.sidabras@cec.mpg.de)
# requires jsidabras/hycohanz as of 20-04-2017
# Loads a file with a list of 1s and 0s and implements it to HFSS as Silv/Vac
# used to load the best results per generation or final 
# ----------------------------------------------
from random import *
import argparse
import hycohanz as hfss

[oAnsoftApp, oDesktop] = hfss.setup_interface()
oProject = hfss.get_active_project(oDesktop)
oDesign = hfss.set_active_design(oProject, 'HFSSDesign1')
oEditor = hfss.set_active_editor(oDesign)
oFieldsReporter = hfss.get_module(oDesign, 'FieldsReporter')

parser = argparse.ArgumentParser(description='Load GA best file and run solution in HFSS.')
parser.add_argument('file', type=str, help='the filename to load')
args = parser.parse_args()

f = open(args.file, 'r')
loadthing = f.readline()
f.close()

print(loadthing)

thing = loadthing.split(", ")

print(thing)
# Drop /n from the end of the list
#thing.pop()

index = 0
Vac = []
Silv = []
for i in thing:
    if i == '1':
        Silv.append("Elm_"+str(index))
        index += 1
    else:
        Vac.append("Elm_"+str(index))
        index += 1

oDesktop.ClearMessages("", "", 3)

# Check if list is empty
if Vac:
    hfss.assign_White(oEditor, Vac)
    hfss.assign_material(oEditor, Vac, MaterialName="vacuum", SolveInside=True)
if Silv:
    hfss.assign_Orange(oEditor, Silv)
    hfss.assign_material(oEditor, Silv, MaterialName="silver", SolveInside=False)

oDesktop.ClearMessages("", "", 3)    
# try:
    #oDesign.Analyze("Setup1")
# except:
    # print("Simulation Error")


oProject.Save()
