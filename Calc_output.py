# ----------------------------------------------
# Script Recorded by ANSYS Electronics Desktop Version 2017.0.0
# 10:00:37  May 09, 2017
# ----------------------------------------------
import ScriptEnv
ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
oDesktop.RestoreWindow()
oProject = oDesktop.SetActiveProject("GA_modify")
oDesign = oProject.SetActiveDesign("HFSSDesign1")
oDesign.Analyze("Setup1")
oModule = oDesign.GetModule("FieldsReporter")
oModule.CopyNamedExprToStack("IntH1r2dVs")
oModule.ClcEval("Setup1 : LastAdaptive", 
	[
		"$i_1:="		, "0",
		"Freq:="		, "9.7GHz",
		"Phase:="		, "0deg"
	])
oModule.CalculatorWrite("B:\\tmp.fld", 
	[
		"Solution:="		, "Setup1 : LastAdaptive"
	], 
	[
		"$i_1:="		, "0",
		"Freq:="		, "9.7GHz",
		"Phase:="		, "0deg"
	])
