# Std
import glob
import os
import shutil  # para borrar el tempdir
import tempfile  # para crear el tempdir
import unittest
from io import StringIO
import numpy

# Mine
import running.sweep
import filesystem.files_aux as files_aux


class TestIndividualSensitivityAnalysis(unittest.TestCase):
    # setup y teardown de los tests
    def setUp(self):
        # Create tempdir and save its path
        self._temp_dir = tempfile.mkdtemp()
        self._temp_files = []  # each test case can create individual files

    def tearDown(self):
        pass
        shutil.rmtree(self._temp_dir)
        for f in self._temp_files:
            f.close()
    # Tests:
    def test_param_values_are_assigned_as_expected(self):
        # Initialize sweep example
        sweep_runner = self.sweepSpecsExample()
        # Get values for each param
        vals_per_param = sweep_runner._valuesPerParam(self._temp_dir)
        correct_vals_per_param = {
            "a": [-1],
            "b": [-0.9, -1.1],
            "c": [-0.85, -1, -1.15],
        }
        for p in correct_vals_per_param:
            p_vals = vals_per_param[p]
            p_correct_vals = correct_vals_per_param[p]
            for v1, v2 in zip(p_vals, p_correct_vals):
                if not v1 == v2:
                    error_msg = "The parameter '{0}' has val {1} when it should have val {2}".format(p, v1, v2)
                    self.fail(error_msg)
    # Auxs
    def sweepSpecsExample(self):
        model_name = "Model"
        model_file_path = os.path.join(self._temp_dir, "model.mo")
        files_aux.writeStrToFile(model_str, model_file_path)
        start_time = 0
        stop_time = 2
        perturbation_info_per_param = [
            {
                "name": "a",
                "delta_percentage": 5,
                "iterations": 1
            },
            {
                "name": "b",
                "delta_percentage": 10,
                "iterations": 2
            },
            {
                "name": "c",
                "delta_percentage": 15,
                "iterations": 3
            },
        ]
        sweep_runner = running.sweep.ParametersSweeper(model_name, model_file_path, start_time, stop_time,
                                                       perturbation_info_per_param)
        return sweep_runner




###########
# Globals #
###########
model_str = \
    """class Model
      parameter Real a=-1;
      parameter Real b=-1;
      parameter Real c=-1;
      Real x(start=1,fixed=true);
    equation
      der(x) = a*x + b/2 + c/4;
    end Model;"""
