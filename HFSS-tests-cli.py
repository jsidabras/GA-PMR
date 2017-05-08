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
from datetime import datetime
startTime = datetime.now()
import re
import shutil
import os
import subprocess

file = "B:\\GA_modify.aedtresults" 
try:
    shutil.rmtree(file)
except:
    pass

files = ["B:\\tmp.fld", "B:\\GA_modify.aedt"]
for file in files:
    try:
        os.remove(file)
    except:
        pass

mat_re = re.compile("MaterialValue")
start_re = re.compile("begin \'ToplevelParts\'")
end_re = re.compile("end \'ToplevelParts\'")
slv_re = re.compile("SolveInside")

randBinList = lambda n: [randint(0,1) for b in range(1,n+1)]

thing = randBinList(1729)

index = 0
list_vac = []
list_pec = []
for i in thing:
    if i == 1:
        list_pec.append("Elm_"+str(index)+"\'")
        index += 1
    else:
        list_vac.append("Elm_"+str(index)+"\'")
        index += 1


        
vac_re = re.compile("|".join(list_vac))
pec_re = re.compile("|".join(list_pec))

file_out = open("GA_modify.aedt", 'w+')
with open("GA_PlanarResonator.aedt", "r") as f:
    flag_start = 0
    flag_vac = 0
    flag_pec = 0
    try:
        for line in f:
            if start_re.search(line):
                file_out.write(line)
                flag_start = 1
            elif end_re.search(line):
                file_out.write(line)
                flag_start = 0
            elif vac_re.search(line) and flag_start == 1:
                flag_vac = 1
                file_out.write(line)
                continue
            elif pec_re.search(line) and flag_start == 1:
                flag_pec = 1
                file_out.write(line)
                continue
            else:
                if flag_vac == 1 and mat_re.search(line):
                    file_out.write(line.replace('pec', 'vacuum'))
                elif flag_vac == 1 and slv_re.search(line):
                    file_out.write(line.replace('false', 'true'))
                    flag_vac = 0
                elif flag_pec == 1 and mat_re.search(line):
                    file_out.write(line.replace('vacuum', 'pec'))
                elif flag_pec == 1 and slv_re.search(line):
                    file_out.write(line.replace('true', 'false'))
                    flag_pec = 0
                else:
                    file_out.write(line)
    except UnicodeDecodeError:
        print("thing")
        
            
file_out.close()


cmdCommand = "ansysedt.exe -ng -BatchSolve GA_modify.aedt"   #specify your cmd command
process = subprocess.Popen(cmdCommand.split(), stdout=subprocess.PIPE, shell=True)
output, error = process.communicate()

cmdCommand = "ansysedt.exe -ng -BatchSave -RunScriptAndExit Calc_output.py GA_modify.aedt"   #specify your cmd command
process = subprocess.Popen(cmdCommand.split(), stdout=subprocess.PIPE, shell=True)
output, error = process.communicate()

with open("B:\\tmp.fld", "r") as out_file:
    for line in out_file:
        try:
            print(float(line))
        except:
            continue


print(datetime.now() - startTime)
