import sys
sys.path.append('/home/omsens/Documents/OMSens/')

import os
import argparse
import json
import pandas as pd
import filesystem.files_aux as files_aux

# Mine
import running.sweep
import plotting.plot_sweep as plot_sweep
from plugin_communication.qt_communicator import QTCommunicator

import logging

# Std
import os
import argparse
import json

# Project
import vectorial.model_optimizer as model_optimizer_f
import modelica_interface.build_model as build_model
import plotting.plot_vectorial as plot_vect_f
from plugin_communication.qt_communicator import QTCommunicator

filehandler = logging.FileHandler("/home/omsens/Documents/results_experiments/logging/vectorial_analysis.log")
logger = logging.getLogger("vectorial_analysis")
logger.addHandler(filehandler)
logger.setLevel(logging.DEBUG)


# Mine
def main():
    logger.debug('Run main (vectorial_analysis)')
    communicator = QTCommunicator(100)
    communicator.set_total_progress_messages(100)
    communicator.update_completed(5)

    # Get arguments from command line call
    json_file_path, dest_folder_path_arg = getCommandLineArguments()

    # Define where to write the results
    if not dest_folder_path_arg:
        dest_folder_path = files_aux.makeOutputPath("vectorial_analysis")
    else:
        dest_folder_path = dest_folder_path_arg

    # Read JSON again (both reads should be refactored into one)
    analyzeFromJSON(dest_folder_path, json_file_path)


def analyzeFromJSON(dest_folder_path, json_file_path):

    # Define destination folder path
    dest_folder_path += "/" + "results/"
    with open(json_file_path, 'r') as fp:
        full_json = json.load(fp)

    # Prepare init args
    model_mo_path = files_aux.moFilePathFromJSONMoPath(full_json["model_mo_path"])

    # Note: Check that the string in 'restriction_path' is effectively a directory'
    base_dir = full_json["restriction_path"]
    results_dirname = base_dir + full_json["model_name"] + '_res.csv'

    # Future work: implement 'intelligent alpha' so that the user doesn't need to iterate every time
    plot_std = full_json["plot_std_run"]
    plot_restriction = full_json["plot_restriction"]

    optim_kwargs = {
        "model_file_path": model_mo_path,
        "build_folder_path": dest_folder_path,

        "target_var_name": full_json["target_var_name"],
        "parameters_to_perturb": full_json["parameters_to_perturb"],
        "model_name": full_json["model_name"],
        "start_time": full_json["start_time"],
        "stop_time": full_json["stop_time"],
        "max_or_min": full_json["max_or_min"],

        "objective_function_name": full_json["objective_function_name"],
        "optimizer_name": full_json["optimizer_name"],
        "alpha_value": full_json["alpha_value"],
        "constrained_time_path_file": full_json["constrained_time_path_file"],
        "constrained_variable": full_json["constrained_variable"],
        "constrained_epsilon": full_json["constrained_epsilon"],

        "base_dir": base_dir,
        "results_dirname": results_dirname
    }
    # logger.debug('Generated optim_kwargs')

    # Initialize builder and compile model:
    # We compile the model again for now to avoid having remnants of the optimization in its compiled model
    plots_folder_name = "plots"
    plots_folder_path = os.path.join(dest_folder_path, plots_folder_name)
    files_aux.makeFolderWithPath(plots_folder_path)

    # Make sub-folder for new model. in Windows we can't use "aux" for folder names
    model_folder_name = "aux_folder"
    model_folder_path = os.path.join(plots_folder_path, model_folder_name)
    files_aux.makeFolderWithPath(model_folder_path)
    model_builder = build_model.ModelicaModelBuilder(full_json["model_name"], full_json["start_time"],
                                                     full_json["stop_time"], model_mo_path)
    compiled_model = model_builder.buildToFolderPath(model_folder_path, base_dir, results_dirname)

    # Run STD Model
    x0_csv_name = "x0_run.csv"
    x0_csv_path = os.path.join(model_folder_path, x0_csv_name)
    x0_dict = {p: compiled_model.defaultParameterValue(p) for p in full_json["parameters_to_perturb"]}
    compiled_model.simulate(x0_csv_path, params_vals_dict=x0_dict)
    df_x0_run = pd.read_csv(x0_csv_path, index_col=False)
    df_x0_run.to_csv(results_dirname, index=False)
    # logger.debug('Generated df_x0_run')

    # Run optimization and re-run with optimal parameters
    model_optimizer = model_optimizer_f.ModelOptimizer(**optim_kwargs)
    # logger.debug('model optimizer generated')

    optim_result = model_optimizer.optimize(full_json["percentage"], full_json["epsilon"])
    x_opt_csv_name = "x_opt_run.csv"
    x_opt_csv_path = os.path.join(model_folder_path, x_opt_csv_name)
    compiled_model.simulate(x_opt_csv_path, params_vals_dict=optim_result.x_opt)
    df_x_opt_run = pd.read_csv(x_opt_csv_path)

    # Update optimum value of 'optim_result'. IMPORTANT: assumes the last contents of csv file is the optimum
    final_optimum_value = df_x_opt_run[full_json["target_var_name"]].tolist()[-1]
    optim_result.target_optimum = final_optimum_value

    # Plot in folder
    var_optimization = full_json["target_var_name"]
    var_restriction = full_json['constrained_variable']
    if plot_std and plot_restriction:
        restriction = pd.read_csv(full_json["constrained_time_path_file"], index_col=False)
        restriction = restriction[restriction['time'] <= df_x_opt_run['time'].max()]
        vect_plotter = plot_vect_f.VectorialPlotter(optim_result, df_x_opt_run, df_x0_run, restriction, var_optimization, var_restriction)
    elif plot_std:
        vect_plotter = plot_vect_f.VectorialPlotter(optim_result, df_x_opt_run, df_x0_run, None, var_optimization, None)
    elif plot_restriction:
        restriction = pd.read_csv(full_json["constrained_time_path_file"], index_col=False)
        restriction = restriction[restriction['time'] <= df_x_opt_run['time'].max()]
        vect_plotter = plot_vect_f.VectorialPlotter(optim_result, df_x_opt_run, None, restriction, var_optimization, var_restriction)
    else:
        raise Exception()

    # Plot
    plot_path = vect_plotter.plotInFolder(plots_folder_path)

    # Prepare JSON output dict
    vect_json_dict = {
        "x0": optim_result.x0,
        "x_opt": optim_result.x_opt,
        "f(x0)": optim_result.f_x0,
        "f(x)_opt": optim_result.target_optimum,
        "stop_time": optim_result.stop_time,
        "variable": optim_result.variable_name,
        "plot_path": plot_path,
    }
    # Write dict as json
    optim_json_str = json.dumps(vect_json_dict, sort_keys=True, indent=2)
    optim_json_file_name = "result.json"
    optim_json_file_path = os.path.join(dest_folder_path, optim_json_file_name)
    files_aux.writeStrToFile(optim_json_str, optim_json_file_path)


# Auxs
def getCommandLineArguments():
    parser = argparse.ArgumentParser(description="vectorial analysis")
    parser.add_argument('test_file_path',
                        metavar='test_file_path',
                        help='The path to the file with the experiment specifications.')
    parser.add_argument('--dest_folder_path',
                        metavar='dest_folder_path',
                        help='Optional: The destination folder where to write the sweep files')
    args = parser.parse_args()
    return args.test_file_path, args.dest_folder_path


# FIRST EXECUTABLE CODE:
if __name__ == "__main__":
    main()

