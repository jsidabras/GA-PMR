#    This file is part of DEAP.
#
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

import hycohanz as hfss
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
    toolbox.attr_bool, 2490)

# define the population to be a list of individuals
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# the goal ('fitness') function to be maximized
def evalOneMax(individual):
    [oAnsoftApp, oDesktop] = hfss.setup_interface()
    oProject = hfss.get_active_project(oDesktop)
    oDesign = hfss.set_active_design(oProject, 'HFSSDesign1')
    oEditor = hfss.set_active_editor(oDesign)
    oFieldsReporter = hfss.get_module(oDesign, 'FieldsReporter')

    index = 0
    Vac = []
    Silv = []
    for i in individual:
        if i == 1:
            Silv.append("Planar_"+str(index))
        else:
            Vac.append("Planar_"+str(index))
        index += 1

    if Vac: 
    # Check if list is empty
    #    hfss.assign_IsModel(oEditor, Vac, IsModel=False)
        hfss.assign_material(oEditor, Vac, MaterialName="vacuum", SolveInside=True)
    if Silv:
    #    hfss.assign_IsModel(oEditor, Silv, IsModel=True)
        hfss.assign_material(oEditor, Silv, MaterialName="silver", SolveInside=False)

    oDesktop.ClearMessages("", "", 3)

    # oProject.Save()
    try:
        oDesign.Analyze("Setup1")
    except:
        print("Simulation Error Set Fitness to 0")
        return 0,

    hfss.enter_qty(oFieldsReporter, 'H')
    hfss.enter_qty(oFieldsReporter, 'H')
    hfss.calc_op(oFieldsReporter, 'Dot')
    hfss.calc_op(oFieldsReporter, 'Real')
    hfss.enter_vol(oFieldsReporter, 'Sample')
    hfss.calc_op(oFieldsReporter, 'Integrate')
    hfss.clc_eval(
        oFieldsReporter,
        'Setup1',
        'LastAdaptive',
        9.7e9,
        0,
        {},
    )
    out = hfss.get_top_entry_value(
        oFieldsReporter,
        'Setup1',
        'LastAdaptive',
        9.7e9,
        0,
        {},
    )
    print(out[0])
    return float(out[0]),

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
    random.seed(64)

    # create an initial population of 300 individuals (where
    # each individual is a list of integers)
    pop = toolbox.population(n=30)

    # CXPB  is the probability with which two individuals
    #       are crossed
    #
    # MUTPB is the probability for mutating an individual
    #
    # NGEN  is the number of generations for which the
    #       evolution runs
    CXPB, MUTPB, NGEN = 0.5, 0.2, 50
    
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
    
    print("-- End of (successful) evolution --")
    
    best_ind = tools.selBest(pop, 1)[0]
    print("Best individual is %s, %s" % (best_ind, best_ind.fitness.values))
    print(datetime.now() - startTime)
    f = open('best_individual', 'w')
    f.write("%s" % (best_ind))
    f.close()

if __name__ == "__main__":
    main()
