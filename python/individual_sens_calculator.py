# STD
import argparse
import json
import logging  # instead of prints
import os
import sys

# Ours
import analysis.indiv_sens
import filesystem.files_aux as files_aux
import mos_writer.calculate_sensitivities_mos_writer as sens_mos_writer
import modelica_interface.run_omc as run_omc
# Setup logging
import settings.gral_settings

logger = logging.getLogger("-Individual Sens Calculator-")
script_description = "Calculate variables sensitivities to parameters when perturbed in isolation"


def main():
    # Logging settings
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    # Get arguments from command line call
    json_file_path, dest_folder_path_arg = getCommandLineArguments()
    # Args
    output_mos_name = "indiv_sens_sims.mos"
    std_run_filename = "std_run.csv"
    dest_folder_path, output_mos_path, std_run_path = filesPathsInOutputFolder(output_mos_name, std_run_filename,
                                                                               dest_folder_path_arg)
    # Create mos script form JSON and write it in dest folder. It returns the paths of the files it will create: std
    #   run, simulated runs, etc
    mos_info = sens_mos_writer.createMosFromJSON(json_file_path, output_mos_path, std_run_filename)
    # Run mos script
    logger.info("Running Modelica with specified information")
<<<<<<< HEAD
    running.run_omc.runMosScript(output_mos_path)
    # Read JSON again (both reads should be refactored into one)
=======
    run_omc.runMosScript(output_mos_path)
    # Read json
>>>>>>> c41cca1605687688524901694774eab65daeaf29
    with open(json_file_path, 'r') as fp:
        full_json = json.load(fp)
    # Prepare analysis inputs from JSON and MOS script info
    analyze_csvs_kwargs = {
        "perturbed_simus_info": mos_info["perturbed_runs"],
        "std_run_csv_path"            : std_run_path,
        "target_vars"                 : full_json["vars_to_analyze"],
        "percentage_perturbed"        : full_json["percentage"],
        "specific_year"               : full_json["stop_time"],
        "output_folder_analyses_path": dest_folder_path,
        "rms_first_year"              : full_json["start_time"],
        "rms_last_year"               : full_json["stop_time"],
    }
    logger.info("Analyzing variable sensitivities to parameters from CSVs")
    # Calculate sensitivities
    analysis_results = analysis.indiv_sens.completeIndividualSensAnalysis(**analyze_csvs_kwargs)
    # Get the dict with the paths
    paths_dict = analysis_results["paths"]
    # Write paths dict as json
    paths_json_str = json.dumps(paths_dict, sort_keys=True, indent=2)
    paths_json_file_name = "paths.json"
    paths_json_file_path = os.path.join(dest_folder_path, paths_json_file_name)
    files_aux.writeStrToFile(paths_json_str, paths_json_file_path)
    logger.info("Finished. The file {0} has all the the analysis files paths.".format(paths_json_file_path))
    return 0


def listOfParametersPerturbationInfo(param_names, param_vals, percentage):
    parameters_to_perturbate_tuples = []
    # Iterate parameters name and default info
    for p_name, p_val in zip(param_names, param_vals):
        # Calculate parameter value from percentage to perturb
        perturbed_val = p_val * (1 + percentage / 100)
        # Create tuple and add it to list of tuples
        param_tuple = (p_name, p_val, perturbed_val)
        parameters_to_perturbate_tuples.append(param_tuple)
    return parameters_to_perturbate_tuples


def filesPathsInOutputFolder(output_mos_name, std_run_filename, dest_folder_path_arg):
    # Make dest folder path in this projects root if none indicated in command line
    if not dest_folder_path_arg:
        dest_folder_path = files_aux.makeOutputPath("indiv_sens_analysis")
    else:
        dest_folder_path = dest_folder_path_arg
    # .mos script
    output_mos_path = os.path.join(dest_folder_path, output_mos_name)
    # Standard run csv
    std_run_path = os.path.join(dest_folder_path, std_run_filename)
    return dest_folder_path, output_mos_path, std_run_path


def csvPathAndParameterNameForFolderAndParametersInfo(dest_folder_path, parameters_info):
    perturbed_csvs_path_and_info_pairs = []
    for param_info in parameters_info:
        param_name = param_info[0]
        csv_name = settings.gral_settings.calc_sens_csv_file_name_function(param_name)
        csv_path = os.path.join(dest_folder_path, csv_name)
        perturbed_csvs_path_and_info_pairs.append((csv_path, param_info))
    return perturbed_csvs_path_and_info_pairs

def getCommandLineArguments():
    parser = argparse.ArgumentParser(description=script_description)
    parser.add_argument('test_file_path', metavar='test_file_path',
                        help='The file path to the test file containing the CSVs to plot, the variables, the title, etc.')
    parser.add_argument('--dest_folder_path', metavar='dest_folder_path',
                        help='Optional: The destination folder where to write the analysis files')
    args = parser.parse_args()
    return args.test_file_path, args.dest_folder_path


# FIRST EXECUTABLE CODE:
if __name__ == "__main__":
    main()

