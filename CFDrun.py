__author__ = "Juri Bieler"
__version__ = "0.0.1"
__status__ = "Development"

import os
import sys

from Gmsh import Gmsh
from Airfoil import Airfoil
from SU2 import SU2
from BPAirfoil import BPAirfoil

GMSH_EXE_PATH = 'gmsh/gmsh.exe'
#SU2_BIN_PATH = 'D:/prog/portable/Luftfahrt/su2-windows-latest/ExecParallel/bin/'
SU2_BIN_PATH = 'su2-windows-latest/ExecParallel/bin/'
OS_MPI_COMMAND = 'mpiexec'
SU2_USED_CORES = 4
WORKING_DIR = 'dataOut/'
INPUT_DIR = 'dataIn/'


class CFDrun:

    def __init__(self, project_name, used_cores=SU2_USED_CORES):
        # create project dir if necessary
        self.projectDir = WORKING_DIR + '/' + project_name
        # create project dir if necessary
        if not os.path.isdir(self.projectDir):
            os.mkdir(self.projectDir)
        self.su2 = SU2(SU2_BIN_PATH, used_cores=used_cores, mpi_exec=OS_MPI_COMMAND)
        self.foilCoord = None
        self.gmsh = Gmsh(GMSH_EXE_PATH)

    def load_airfoil_from_file(self, file_name):
        foil = Airfoil(file_name)
        self.foilCoord = foil.get_sorted_point_list()

    #def load_airfoil_bp(self):
    #    bp = BPAirfoil()
    #    self.foilCoord = bp.generate_airfoil(500, show_plot=False)

    def set_airfoul_coords(self, coords):
        self.foilCoord = coords

    def generate_mesh(self):
        print('start meshing...')
        self.gmsh.generate_geo_file(self.foilCoord, 'airfoilMesh.geo', 1000, working_dir=self.projectDir)
        self.gmsh.run_2d_geo_file('airfoilMesh.geo', 'airfoilMesh.su2', working_dir=self.projectDir)

    def su2_fix_mesh(self):
        print('start mesh-fixing...')
        self.su2.fix_mesh('airfoilMesh.su2', 'airfoilMeshFixed.su2', working_dir=self.projectDir)

    def su2_solve(self, config):
        print('start solving...')
        self.su2.run_cfd('airfoilMeshFixed.su2', config, working_dir=self.projectDir)

    def su2_parse_results(self):
        print('parse results...')
        totalCL, totalCD, totalCM, totalE = self.su2.parse_force_breakdown('forces_breakdown.dat', working_dir=self.projectDir)
        return totalCL, totalCD, totalCM, totalE

    def clean_up(self):
        print('clean up...')
        if os.path.isfile(self.projectDir + '/airfoilMesh.su2'):
            os.remove(self.projectDir + '/airfoilMesh.su2')
        if os.path.isfile(self.projectDir + '/airfoilMeshFixed.su2'):
            os.remove(self.projectDir + '/airfoilMeshFixed.su2')
        if os.path.isfile(self.projectDir + '/cfdMpiRun.bat'):
            os.remove(self.projectDir + '/cfdMpiRun.bat')
        if os.path.isfile(self.projectDir + '/restart_flow.dat'):
            os.remove(self.projectDir + '/restart_flow.dat')
        if os.path.isfile(self.projectDir + '/original_grid.dat'):
            os.remove(self.projectDir + '/original_grid.dat')
        if os.path.isfile(self.projectDir + '/meshFix.cfg'):
            os.remove(self.projectDir + '/meshFix.cfg')