#Std
import unittest
import os
import tempfile #para crear el tempdir
import shutil #para borrar el tempdir
import re #para los regex
from io import StringIO
# Mine
import analysis.indiv_sens

class TestIndividualSensitivityAnalysis(unittest.TestCase):
#setup y teardown de los tests
    def setUp(self):
        #Create tempdir and save its path
        self._temp_dir = tempfile.mkdtemp()
        self._temp_files = [] #each test case can create individual files
    def tearDown(self):
        pass
        shutil.rmtree(self._temp_dir)
        for f in self._temp_files:
            f.close()
# Tests:
    def test_sens_run_gives_correct_results(self):
        # We test everything on this test for now
        analyze_csvs_kwargs = {
            "perturbed_csvs_path_and_info_pairs" : [(StringIO(bb_e_perturbed_str), ('e', 0.7, 0.735)), (StringIO(bb_g_perturbed_str), ('g', 9.81, 10.300500000000001))],
            "std_run_csv_path"                   : StringIO(bb_std_run_str),
            "target_vars"                        : ['h'],
            "percentage_perturbed"               : 5,
            "specific_year"                      : 3,
            "output_folder_analyses_path"        : self._temp_dir,
            "rms_first_year"                     : 0,
            "rms_last_year"                      : 3,
        }
        analysis_files_paths = analysis.indiv_sens.completeIndividualSensAnalysis(**analyze_csvs_kwargs)
        # Test that that the resulting run info includes the basic info: all param names, default and perturbed vals, the variable and its value
        run_infos_per_var = analysis_files_paths["run_infos_per_var"]
        # for t_var in analyze_csvs_kwargs["target_vars"]:

###########
# Globals #
###########
bb_std_run_str = \
""""time","h","v","der(h)","der(v)","v_new","flying","impact"
0,1,0,0,-9.81,0,1,0
1,0.2250597607429705,-2.279940238910565,-2.279940238910565,-9.81,3.100612842801532,1,0
2,0.04243354772647411,-0.5463586255141026,-0.5463586255141026,-9.81,1.063510205007515,1,0
3,2.101988323055078e-11,0,0,0,0,0,1"""

bb_e_perturbed_str = \
""""time","h","v","der(h)","der(v)","v_new","flying","impact"
0,1,0,0,-9.81,0,1,0
1,0.3100904028764322,-2.124909596770488,-2.124909596770488,-9.81,3.255643484941609,1,0
2,0.04233293611696021,0.9167931152103947,0.9167931152103947,-9.81,1.292703301139997,1,0
3,2.631538447381662e-11,0,0,0,0,0,1"""

bb_g_perturbed_str = \
""""time","h","v","der(h)","der(v)","v_new","flying","impact"
0,1,0,0,-10.3005,0,1,0
1,0.1657651633154364,-2.584484836337927,-2.584484836337927,-10.3005,3.177182714449088,1,0
2,0.003483617140901725,-1.056333590801138,-1.056333590801138,-10.3005,1.089773670982276,1,0
3,2.105894579818758e-11,0,0,0,0,0,1"""
