# ----------------------------------------------
# Script Recorded by ANSYS Electronics Desktop Version 2017.0.0
# 10:48:48  May 08, 2017
# ----------------------------------------------
import ScriptEnv
ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
oDesktop.RestoreWindow()
oProject = oDesktop.SetActiveProject("GA_PlanarResonator")
oDesign = oProject.SetActiveDesign("HFSSDesign1")
oModule = oDesign.GetModule("FieldsReporter")
oModule.CopyNamedExprToStack("IntH1r2dVs")
oModule.ClcEval("Setup1 : LastAdaptive", 
	[
		"$i_1:="		, "0",
		"Freq:="		, "9.7GHz",
		"Phase:="		, "0deg"
	])
return oModule.GetTopEntryValue("Setup1 : LastAdaptive", 
	[
		"$i_1:="		, "0",
		"Freq:="		, "9.7GHz",
		"Phase:="		, "0deg"
	])