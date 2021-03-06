
#    DEAP is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of
#    the License, or (at your option) any later version.
#
#    DEAP is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with DEAP. If not, see <http://www.gnu.org/licenses/>.



#    Highly modified by Jason W. Sidabras jason.sidabras@cec.mpg.de
#    maximize H field in a sample and maximize the uniformity
#    this is used to find non-obvious solutions to the planar micro resonator
#    turns elements to silver (1) or vacuum (0)

import random

from deap import base
from deap import creator
from deap import tools

import hycohanz as hfss
import shutil
from datetime import datetime
startTime = datetime.now()


creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, typecode='f', fitness=creator.FitnessMax)

toolbox = base.Toolbox()

# Attribute generator
#                      define 'attr_bool' to be an attribute ('gene')
#                      which corresponds to integers sampled uniformly
#                      from the range [0,1] (i.e. 0 or 1 with equal
#                      probability)
toolbox.register("attr_bool", random.randint, 0, 1)

# Structure initializers
#                         define 'individual' to be an individual
#                         consisting of 2490 'attr_bool' elements ('genes')
toolbox.register("individual", tools.initRepeat, creator.Individual,
    toolbox.attr_bool, 1767)

# define the population to be a list of individuals
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# colorize the solution for visual of generation
def colorize_best(individual):
    [oAnsoftApp, oDesktop] = hfss.setup_interface()
    oProject = hfss.get_active_project(oDesktop)
    oDesign = hfss.set_active_design(oProject, 'HFSSDesign1')
    oEditor = hfss.set_active_editor(oDesign)

    index = 0
    Vac = []
    Silv = []
    for i in individual:
        if i == 1:
            Silv.append("Elm_"+str(index))
        else:
            Vac.append("Elm_"+str(index))
        index += 1  
    
    hfss.assign_White(oEditor, Vac)
    hfss.assign_Orange(oEditor, Silv)
    
# the goal ('fitness') function to be maximized
def evalOneMax(individual):
    [oAnsoftApp, oDesktop] = hfss.setup_interface()
    oProject = hfss.get_active_project(oDesktop)
    oDesign = hfss.set_active_design(oProject, 'HFSSDesign1')
    oEditor = hfss.set_active_editor(oDesign)
    oFieldsReporter = hfss.get_module(oDesign, 'FieldsReporter')
    oSolution = oDesign.GetModule("Solutions")

    # Shut off autosave to minimize the .adresults folder
    oDesktop.EnableAutoSave(False)

    index = 0
    Vac = []
    Silv = []
    for i in individual:
        if i == 1:
            Silv.append("Elm_"+str(index))
        else:
            Vac.append("Elm_"+str(index))
        index += 1

    # Check if list is empty
    if Vac:
        #hfss.assign_IsModel(oEditor, Vac, IsModel=False)
        hfss.assign_material(oEditor, Vac, MaterialName="vacuum", SolveInside=True)
    if Silv:
        # hfss.assign_IsModel(oEditor, Silv, IsModel=True)
        hfss.assign_material(oEditor, Silv, MaterialName="pec", SolveInside=False)

    oDesktop.ClearMessages("", "", 3)
    # Purge History to minimize the solution time and minimize the .adresults folder
    # Is this needed every time? Modeler -> PurgeHistory
    #oEditor.PurgeHistory(["NAME:Selections", "Selections:=", Silv, "NewPartsModelFlag:=", "Model"])
    #oEditor.PurgeHistory(["NAME:Selections", "Selections:=", Vac, "NewPartsModelFlag:=", "Model"])

    # Solutions results purge with shutil.rmtree
    folder = "B:\\GA_PlanarResonator.aedtresults\\HFSSDesign1.results"
    shutil.rmtree(folder)
    # Try to solve, if there is an error send it to zero. 
    # ISSUE: If the RAMDisk is full this gives an error and sends everything to zero
    # should be fixed with the PurgeHistory and AutoSave off... ??
    # Autosave off helps, but shutil.rmtree is needed
    try:
        oDesign.Analyze("Setup1")
    except:
        print("Simulation Error Set Fitness -10000, ")
        return -10000, 
        
    oFieldsReporter.CalcStack('clear')
    # Load the pre solved calculator expressions. Some will delete when Fastlist is deleted
    # Remember to set Ple to zero unless you are solving for the losses in the substrate
    #oFieldsReporter.LoadNamedExpressions("E:\\MPI\\Maxwell\\Projects\\PersonalLib\\_Signal_14 - Xband - ICE.clc", "Fields", ["ImDieHold", "ImDieSam", "Frq", "H1r", "H1rMax", "IntH1r2dVs"])
    oFieldsReporter.CopyNamedExprToStack("IntH1r2dVs")
    # Is there a solution present? If so clc_eval if not, run the Analyze again
    # if there is still no solution, send it to zero
    if oSolution.HasFields("Setup1:LastAdaptive", "x_size=2mm") == 1:
        hfss.clc_eval(
            oFieldsReporter,
            'Setup1',
            'LastAdaptive',
            9.7e9,
            0,
            {},
        )
    else:
        oDesign.Analyze("Setup1")
        try:
            hfss.clc_eval(
                oFieldsReporter,
                'Setup1',
                'LastAdaptive',
                9.7e9,
                0,
                {},
            )
        except:
            print("Simulation Error Set Fitness -1000, ")
            return -1000, 
    outH = hfss.get_top_entry_value(
        oFieldsReporter,
        'Setup1',
        'LastAdaptive',
        9.7e9,
        0,
        {},
    )

    #oFieldsReporter.CopyNamedExprToStack("EdVs")
    # Is there a solution present? If so clc_eval if not, run the Analyze again
    # if there is still no solution, send it to zero
    # if oSolution.HasFields("Setup1:LastAdaptive", "x_size=2mm") == 1:
        # hfss.clc_eval(
            # oFieldsReporter,
            # 'Setup1',
            # 'LastAdaptive',
            # 9.7e9,
            # 0,
            # {},
        # )
    # else:
        # oDesign.Analyze("Setup1")
        # try:
            # hfss.clc_eval(
                # oFieldsReporter,
                # 'Setup1',
                # 'LastAdaptive',
                # 9.7e9,
                # 0,
                # {},
            # )
        # except:
            # print("Simulation Error Set Fitness -1, ")
            # return -1, 
    # outE = hfss.get_top_entry_value(
        # oFieldsReporter,
        # 'Setup1',
        # 'LastAdaptive',
        # 9.7e9,
        # 0,
        # {},
    # )
    
    # print(outH[0] + ", " + outE[0])
    print(outH[0])
    print("Time: " + str(datetime.now() - startTime))
    return float(outH[0]),

#----------
# Operator registration
#----------
# register the goal / fitness function
toolbox.register("evaluate", evalOneMax)

# register the crossover operator
toolbox.register("mate", tools.cxTwoPoint)

# register a mutation operator with a probability to
# flip each attribute/gene of 0.05
toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)

# operator for selecting individuals for breeding the next
# generation: each individual of the current generation
# is replaced by the 'fittest' (best) of three individuals
# drawn randomly from the current generation.
toolbox.register("select", tools.selTournament, tournsize=3)

#----------

def main():
    random.seed(42)

    # create an initial population of 300 individuals (where
    # each individual is a list of integers)

    pop = toolbox.population(n=40)

    # CXPB  is the probability with which two individuals
    #       are crossed
    #
    # MUTPB is the probability for mutating an individual
    #
    # NGEN  is the number of generations for which the
    #       evolution runs
    CXPB, MUTPB, NGEN = 0.55, 0.3, 30

    print("Start of evolution")

    # Evaluate the entire population
    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit

    print("  Evaluated %i individuals" % len(pop))

    # Begin the evolution
    for g in range(NGEN):
        print("-- Generation %i --" % g)

        # Select the next generation individuals
        offspring = toolbox.select(pop, len(pop))
        # Clone the selected individuals
        offspring = list(map(toolbox.clone, offspring))

        # Apply crossover and mutation on the offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):

            # cross two individuals with probability CXPB
            if random.random() < CXPB:
                toolbox.mate(child1, child2)

                # fitness values of the children
                # must be recalculated later
                del child1.fitness.values
                del child2.fitness.values

        for mutant in offspring:

            # mutate an individual with probability MUTPB
            if random.random() < MUTPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        print("  Evaluated %i individuals" % len(invalid_ind))

        # The population is entirely replaced by the offspring
        pop[:] = offspring

        # Gather all the fitnesses in one list and print the stats
        fits = [ind.fitness.values[0] for ind in pop]

        length = len(pop)
        mean = sum(fits) / length
        sum2 = sum(x*x for x in fits)
        std = abs(sum2 / length - mean**2)**0.5

        print("  Min %s" % min(fits))
        print("  Max %s" % max(fits))
        print("  Avg %s" % mean)
        print("  Std %s" % std)
        # Save progress
        best_ind = tools.selBest(pop, 1)[0]
        f = open('./Solutions/' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '_best_individual_Gen_' + str(g), 'w')
        f.write("%s\n" % (best_ind))
        f.write("  Max %s" % max(fits))
        f.close()
        # Colorize the best solution 
        # colorize_best(best_ind)
        print("Time: " + str(datetime.now() - startTime))

    print("-- End of (successful) evolution --")

    best_ind = tools.selBest(pop, 1)[0]
    print("Best individual is %s, %s" % (best_ind, best_ind.fitness.values))
    print(datetime.now() - startTime)
    # Save best individual final
    f = open('./Solutions/' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '_best_individual_Final', 'w')
    f.write("%s\n" % (best_ind))
    f.write("  Max %s" % max(fits))
    f.close()
    
    # Colorize the final best individual 
    colorize_best(best_ind)

if __name__ == "__main__":
    main()
