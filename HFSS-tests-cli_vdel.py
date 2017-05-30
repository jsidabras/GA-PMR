# ----------------------------------------------
# Script Written by Jason W. Sidabras (jason.sidabras@cec.mpg.de)
# requires jsidabras/hycohanz as of 20-04-2017
# 20-04-2017: script runs 3m00s for 2490 element change. Hfss-Region 
# (Model/NonModel change) Vacuum can produce non-solvable geometries. Meshed 1 pass
# 20-04-2017: script runs 3m12s for 2490 element change. Removed hfss-Region 
# and replaced with a static subtracted vacuum volume (Model/NonModel change).
# 19-04-2017: script runs 4m44s for 2490 element change (material change). 
# 05-05-2017: rewritten to not use hycohanz runs everything from cli
# 11-05-2017: now turns elements to silver (1) or deletes them (0)
# ----------------------------------------------
from random import *
from datetime import datetime
startTime = datetime.now()
import re
import shutil
import os
import subprocess

mat_re = re.compile("MaterialValue")
start_re = re.compile("begin \'ToplevelParts\'")
end_re = re.compile("end \'ToplevelParts\'")
slv_re = re.compile("SolveInside")

randBinList = lambda n: [randint(0,1) for b in range(1,n+1)]

thing = randBinList(6012)

# file = "B:\\GA_modify2D.aedtresults" 
# try:
    # shutil.rmtree(file)
# except:
    # pass

# files = ["B:\\tmp2.fld", "B:\\GA_modify2D.aedt", "B:\\GA_modify2D.aedt.lock"]
# for file in files:
    # try:
        # os.remove(file)
    # except:
        # pass

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

file_out = open("GA_modify2D.aedt", 'wb+')
with open("GA_PlanarResonator2D.aedt", "rb") as f:
    flag_start = 0
    flag_pec = 0
    try:
        for line in f:
            try:
                line = line.decode('utf-8')
            except:
                file_out.write(line)
                continue
            if start_re.search(line):
                file_out.write(line.encode('utf-8'))
                flag_start = 1
                continue
            elif end_re.search(line):
                file_out.write(line.encode('utf-8'))
                flag_start = 0
            elif vac_re.search(line) and flag_start == 1:
                file_out.write(line.replace('Name', 'Nme').encode('utf-8'))
                continue
            elif pec_re.search(line) and flag_start == 1:
                flag_pec = 1
                file_out.write(line.replace('Nme', 'Name').encode('utf-8'))
                continue
            else:
                if flag_pec == 1 and mat_re.search(line):
                    file_out.write(line.replace('vacuum', 'pec').encode('utf-8'))
                elif flag_pec == 1 and slv_re.search(line):
                    file_out.write(line.replace('true', 'false').encode('utf-8'))
                    flag_pec = 0
                else:
                    file_out.write(line.encode('utf-8'))
    except UnicodeDecodeError:
        print("thing")  

file_out.close()



print(datetime.now() - startTime)
