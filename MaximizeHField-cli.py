
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


#    example which maximizes the sum of a list of integers
#    each of which can be 0 or 1

import random

from deap import base
from deap import creator
from deap import tools

import shutil
import os
import re
import subprocess

mat_re = re.compile("MaterialValue")
start_re = re.compile("begin \'ToplevelParts\'")
end_re = re.compile("end \'ToplevelParts\'")
slv_re = re.compile("SolveInside")

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

def evalOneMax(individual):
    # Solutions results purge with shutil.rmtree
    file = "B:\\GA_modify.aedtresults" 
    try:
        shutil.rmtree(file)
    except:
        pass

    files = ["B:\\tmp.fld", "B:\\GA_modify.aedt", "B:\\GA_modify.aedt.lock"]
    for file in files:
        try:
            os.remove(file)
        except:
            pass

    index = 0
    list_vac = []
    list_pec = []
    for i in individual:
        if i == 1:
            list_pec.append("Elm_"+str(index)+"\'")
            index += 1
        else:
            list_vac.append("Elm_"+str(index)+"\'")
            index += 1


            
    vac_re = re.compile("|".join(list_vac))
    pec_re = re.compile("|".join(list_pec))

    file_out = open("GA_modify.aedt", 'wb+')
    with open("GA_PlanarResonator.aedt", "rb") as f:
        flag_start = 0
        flag_vac = 0
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
                elif end_re.search(line):
                    file_out.write(line.encode('utf-8'))
                    flag_start = 0
                elif vac_re.search(line) and flag_start == 1:
                    flag_vac = 1
                    file_out.write(line.encode('utf-8'))
                    continue
                elif pec_re.search(line) and flag_start == 1:
                    flag_pec = 1
                    file_out.write(line.encode('utf-8'))
                    continue
                else:
                    if flag_vac == 1 and mat_re.search(line):
                        file_out.write(line.replace('pec', 'vacuum').encode('utf-8'))
                    elif flag_vac == 1 and slv_re.search(line):
                        file_out.write(line.replace('false', 'true').encode('utf-8'))
                        flag_vac = 0
                    elif flag_pec == 1 and mat_re.search(line):
                        file_out.write(line.replace('vacuum', 'pec').encode('utf-8'))
                    elif flag_pec == 1 and slv_re.search(line):
                        file_out.write(line.replace('true', 'false').encode('utf-8'))
                        flag_pec = 0
                    else:
                        file_out.write(line.encode('utf-8'))
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
                output = float(line)
                break
            except:
                continue
    
    print("Time: " + str(datetime.now() - startTime))
    return output,

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

    pop = toolbox.population(n=60)

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
