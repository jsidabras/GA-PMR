# ----------------------------------------------
# Script Recorded by ANSYS Electronics Desktop Version 2017.0.0
# 15:00:54  May 30, 2017
# ----------------------------------------------
import ScriptEnv
ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
oDesktop.RestoreWindow()
oProject = oDesktop.SetActiveProject("Test")
oDesign = oProject.SetActiveDesign("EMDesign1")
oEditor = oDesign.SetActiveEditor("Layout")

f = open("B:\\individual.tmp", 'r')
loadthing = f.readline()
f.close()

dump = loadthing.strip("[")
dump = dump.rstrip()
dump = dump.strip(r"']").split(", ")
thing = []
for i in dump:
    thing.append(int(i))

print(len(dump))
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

command_thing = ["NAME:AllTabs"]
to = ["NAME:PropServers"]
to.extend(Silv)
g_thing = ["NAME:BaseElementTab"]
g_thing.append(to)
g_thing.append(["NAME:ChangedProps",["NAME:PlacementLayer","Value:=", "Top"]])
command_thing.append(g_thing)
oEditor.ChangeProperty(command_thing)        

command_thing = ["NAME:AllTabs"]
to = ["NAME:PropServers"]
to.extend(Vac)
g_thing = ["NAME:BaseElementTab"]
g_thing.append(to)
g_thing.append(["NAME:ChangedProps",["NAME:PlacementLayer","Value:=", "Gnd"]])
command_thing.append(g_thing)
oEditor.ChangeProperty(command_thing)         
        
oDesign.Analyze("HFSS Setup 1")

oModule = oDesign.GetModule("FieldsReporter")
oModule.EnterQty("H")
oModule.CalcStack("push")
oModule.CalcOp("Conj")
oModule.CalcOp("Dot")
oModule.CalcOp("Real")
try:
    oModule.ExportOnGrid("B:\\tmp.fld", ["0meter", "0meter", "-1mm"], ["0meter", "0meter", "1mm"], ["0.1meter", "0.1meter", "0.1mm"], "HFSS Setup 1 : Last Adaptive", 
        [
            "F:="			, "9.7GHz",
            "Phase:="		, "0deg"
        ], True, "Cartesian", ["0meter", "0meter", "0meter"], False)
except:
    print ("Failed solution")    