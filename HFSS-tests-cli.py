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
import subprocess

mat_re = re.compile("MaterialValue")
start_re = re.compile("begin \'ToplevelParts\'")
end_re = re.compile("end \'ToplevelParts\'")

randBinList = lambda n: [randint(0,1) for b in range(1,n+1)]

thing = randBinList(10)

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
with open("GA_PlanarResonator.aedt") as f:
    flag_start = 0
    flag_vac = 0
    flag_pec = 0
    for line in f:
        if start_re.search(line):
            flag_start = 1
        elif end_re.search(line):
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
                flag_vac = 0
            elif flag_pec == 1 and mat_re.search(line):
                file_out.write(line.replace('vacuum', 'pec'))
                flag_pec = 0
            else:
                file_out.write(line)
file_out.close()

cmdCommand = "ansysedt.exe -ng -local -batchsolve -batchextract Calc_output.py GA_modify.aedt"   #specify your cmd command
process = subprocess.Popen(cmdCommand.split(), stdout=subprocess.PIPE)
output, error = process.communicate()
print output

print(datetime.now() - startTime)
