
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
#    maximize H field in a sample
#    this is used to find non-obvious solutions to the planar micro resonator
#    turns elements to silver (1) or vacuum (0)

import random

from deap import base
from deap import creator
from deap import tools

import shutil
import os
import re
import subprocess

import hycohanz as hfss


mat_re = re.compile("0.0000000000000000e\+000 0.0000000000000000e\+000 1.0000000000000005e-004 (?P<num>\W.+)")


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
    toolbox.attr_bool, 2264)

# define the population to be a list of individuals
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# colorize the solution for visual of generation

def evalOneMax(individual):
    # Solutions results purge with shutil.rmtree
    # file = "B:\\GA_modify2D.aedtresults" 
    # try:
        # shutil.rmtree(file)
    # except:
        # pass
    # Purge files that are no longer needed for newest solution
    files = ["B:\\tmp.fld"]
    for file in files:
        try:
            os.remove(file)
        except:
            pass
    [oAnsoftApp, oDesktop] = hfss.setup_interface()
    oProject = hfss.get_active_project(oDesktop)
    oDesign = oProject.SetActiveDesign("EMDesign1")
    oEditor = oDesign.SetActiveEditor("Layout")

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
    
    # cmdCommand = "ansysedt.exe -WaitForLicense -RunScriptAndExit Calc_output_EMDesign.py -BatchSave Test.aedt"   #specify your cmd command
    # process = subprocess.Popen(cmdCommand.split(), stdout=subprocess.PIPE, shell=True)
    # output, error = process.communicate()

    oDesign.AnalyzeAll()
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
        print ("No tmp.fld, failed solution?")
        return 0,    
    try:
        with open("B:\\tmp.fld", "r") as out_file:
            for line in out_file:
                if mat_re.search(line):
                    output = mat_re.search(line).group('num')
                    print(output)
        

        return float(output),
    except:
        print ("No tmp.fld, failed solution?")
        return 0,

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

    pop = toolbox.population(n=300)

    # CXPB  is the probability with which two individuals
    #       are crossed
    #
    # MUTPB is the probability for mutating an individual
    #
    # NGEN  is the number of generations for which the
    #       evolution runs
    CXPB, MUTPB, NGEN = 0.55, 0.25, 30

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
        f = open('E:\\Dropbox\\_WorkingDir\\GA-PMR\\Solutions\\' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '_best_individual_Gen_' + str(g), 'w+')
        f.write("%s\n" % (best_ind))
        f.write("  Max %s" % max(fits))
        f.close()

        print("Time: " + str(datetime.now() - startTime))

    print("-- End of (successful) evolution --")

    best_ind = tools.selBest(pop, 1)[0]
    print("Best individual is %s, %s" % (best_ind, best_ind.fitness.values))
    print(datetime.now() - startTime)
    # Save best individual final
    f = open('E:\\Dropbox\\_WorkingDir\\GA-PMR\\Solutions\\' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '_best_individual_Gen_Final', 'w+')
    f.write("%s\n" % (best_ind))
    f.write("  Max %s" % max(fits))
    f.close()


if __name__ == "__main__":
    main()
