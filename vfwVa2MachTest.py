__author__ = "Juri Bieler"
__version__ = "0.0.1"
__status__ = "Development"

import os
import sys
import math
from datetime import datetime

from Gmsh import Gmsh
from Airfoil import Airfoil
from SU2 import SU2
from BPAirfoil import BPAirfoil
from CFDrun import CFDrun
from constants import *

from openmdao.core.explicitcomponent import ExplicitComponent
from openmdao.api import Problem, ScipyOptimizeDriver, IndepVarComp, ExplicitComponent
import matplotlib.pyplot as plt
import numpy as np

from openmdao.core.problem import Problem
from openmdao.core.group import Group
from openmdao.core.indepvarcomp import IndepVarComp
from openmdao.core.analysis_error import AnalysisError

# create working dir if necessary
if not os.path.isdir(WORKING_DIR):
    os.mkdir(WORKING_DIR)

# check if gmsh exe exists
if not os.path.isfile(GMSH_EXE_PATH):
    print('gmsh executable could not be found in: ' + GMSH_EXE_PATH)
    sys.exit(0)

#create working dir if necessary
if not os.path.isdir(WORKING_DIR):
    os.mkdir(WORKING_DIR)

#check if gmsh exe exists
if not os.path.isfile(GMSH_EXE_PATH):
    print('gmsh executable could not be found in: ' + GMSH_EXE_PATH)
    sys.exit(0)


### default config for SU2 run ###
config = dict()
config['PHYSICAL_PROBLEM'] = 'EULER'
config['AOA'] = str(0.)
config['MACH_NUMBER'] = str(0.75)
config['FREESTREAM_PRESSURE'] = str(24999.8) #for altitude 10363 m
config['FREESTREAM_TEMPERATURE'] = str(220.79) #for altitude 10363 m
#config['GAS_CONSTANT'] = str(287.87)
#config['REF_LENGTH'] = str(1.0)
#config['REF_AREA'] = str(1.0)
config['MARKER_EULER'] = '( airfoil )'
config['MARKER_FAR'] = '( farfield )'
config['EXT_ITER'] = str(9999)
config['OUTPUT_FORMAT'] = 'PARAVIEW'

REF_LENGTH = 4.
REF_AREA = 1.
REYNOLD = 6e6
config['REF_LENGTH'] = str(REF_LENGTH)
config['REF_AREA'] = str(REF_AREA)
config['REYNOLDS_NUMBER'] = str(REYNOLD)
config['REYNOLDS_LENGTH'] = str(1.)




##################################
### naca Test ca, cd over mach ###

su2 = SU2(SU2_BIN_PATH, used_cores=SU2_USED_CORES, mpi_exec=OS_MPI_COMMAND)

machNr = range(60, 82, 2)
machNr = [75]
aoa = aoa = np.linspace(-4, 6, 51)
aoa = [0.]

ouputF = open(WORKING_DIR + '/' + 'machResult_' + datetime.now().strftime('%Y-%m-%d_%H_%M_%S') + '.csv', 'w')
ouputF.write('machNr,AOA,CL,CD,CM,E,Iterations,Time(min)\n')

for mach in machNr:
    for a in aoa:

        projectName = 'vfw-va2Mach_%03d_%03d' % (mach, a * 100)
        projectDir = WORKING_DIR + '/' + projectName
        #create project dir if necessary
        if not os.path.isdir(projectDir):
            os.mkdir(projectDir)

        cfd = CFDrun(projectName, used_cores=SU2_USED_CORES)

        cfd.load_airfoil_from_file(INPUT_DIR + '/vfw-va2.dat')
        #cfd.construct2d_generate_mesh(scale=REF_LENGTH)
        cfd.gmsh_generate_mesh(scale=REF_LENGTH)
        cfd.su2_fix_mesh()

        config['MACH_NUMBER'] = str(mach / 100.)
        config['AOA'] = str(a)
        cfd.su2_solve(config)

        totalCL, totalCD, totalCM, totalE = cfd.su2_parse_results()

        print('totalCL: ' + str(totalCL))
        print('totalCD: ' + str(totalCD))
        results = cfd.su2_parse_iteration_result()
        # totalCL, totalCD, totalCM, totalE = cfd.su2_parse_results()
        totalCL = results['CL']
        totalCD = results['CD']
        totalCM = results['CMz']
        totalE = results['CL/CD']
        ouputF.write(str(mach / 100.) + ','
                     + str(a) + ','
                     + str(totalCL) + ','
                     + str(totalCD) + ','
                     + str(totalCM) + ','
                     + str(totalE) + ','
                     + str(results['Iteration']) + ','
                     + str(results['Time(min)']) + '\n')
        ouputF.flush()

tCL = []
tCD = []
plt.close()
plt.clf()
for mach in machNr:
    projectDir = WORKING_DIR + '/' 'vfw-va2Mach' + '%03d' % mach
    totalCL, totalCD, totalCM, totalE = su2.parse_force_breakdown('forces_breakdown.dat', working_dir=projectDir)
    tCL.append(totalCL)
    tCD.append(totalCD)

plt.plot(machNr, tCD, '-r')
plt.plot(machNr, tCL, '-b')
plt.show()
