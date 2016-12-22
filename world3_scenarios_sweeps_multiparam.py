# Std:
import os
import sys
import logging #en reemplazo de los prints
import functools # for reduce
logger = logging.getLogger("--World3 scenarios sweep--") #un logger especifico para este modulo
logger = logging.getLogger("--World3 scenarios Multiparameter sweep --") #un logger especifico para este modulo

#Mine:
import settings.settings_world3_sweep as world3_settings
import mos_writer.formulas as predef_formulas
import mos_writer.parameter_sweep_settings as parameter_sweep_settings
import mos_writer.mos_script_factory
import filesystem.files_aux as files_aux
import settings.gral_settings as gral_settings
import running.run_omc
import sweeping.iterationInfo
import readme_writer.readme_writer as readme_writer
import plotting.plot_csv as plot_csv

vanilla_SysDyn_mo_path               = world3_settings._sys_dyn_package_vanilla_path.replace("\\","/") # The System Dynamics package without modifications
piecewiseMod_SysDyn_mo_path          = world3_settings._sys_dyn_package_pw_fix_path.replace("\\","/") # Piecewise function modified to accept queries for values outside of range. Interpolate linearly using closest 2 values
populationTankNewVar_SysDyn_mo_path  = world3_settings._sys_dyn_package_pop_state_var_new.replace("\\","/") # Added a new "population" var that includes an integrator. Numerically it's the same as "population" but with the advantage that now we can calculate sensitivities for it
Run2vermeulenAndJongh_SysDyn_mo_path = world3_settings._sys_dyn_package_v_and_j_run_2.replace("\\","/") # Added a new "population" var that includes an integrator. Numerically it's the same as "population" but with the advantage that now we can calculate sensitivities for it
Run3vermeulenAndJongh_SysDyn_mo_path = world3_settings._sys_dyn_package_v_and_j_run_3.replace("\\","/") # Added a new "population" var that includes an integrator. Numerically it's the same as "population" but with the advantage that now we can calculate sensitivities for it
pseudoffwparam_SysDyn_mo_path        = world3_settings._sys_dyn_package_pseudo_ffw_param_path.replace("\\","/") # Added a new "population" var that includes an integrator. Numerically it's the same as "population" but with the advantage that now we can calculate sensitivities for it

def main():
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
#### WORK PACKAGE 3 ####
    test3Params()

def test3Params():

    # Declare each parameter settings separately and then add them to the list manually
    inExAvgTim_sweepSettings   = parameter_sweep_settings.OrigParameterSweepSettings("income_expect_avg_time" , predef_formulas.DeltaBeforeAndAfter(0.01) , 5) # (param_name , formula_instance , iterations)
    indCapOutRat_sweepSettings = parameter_sweep_settings.OrigParameterSweepSettings("p_ind_cap_out_ratio_1"  , predef_formulas.IncreasingByPercentage(5) , 2) # (param_name , formula_instance , iterations)
    nrRes_sweepSettings        = parameter_sweep_settings.OrigParameterSweepSettings("nr_resources_init"      , predef_formulas.DeltaBeforeAndAfter(0.1)  , 5) # (param_name , formula_instance , iterations)
    sweep_params_settings_list = [ inExAvgTim_sweepSettings, indCapOutRat_sweepSettings,nrRes_sweepSettings]

    run_kwargs = {
    "sweep_params_settings_list" : sweep_params_settings_list,
    "plot_vars"             : ["population"],
    "stopTime"              : 2500  ,# year to end the simulation (2100 for example)
    "scens_to_run"          : [1], #The standard run corresponds to the first scenario
    "fixed_params"          : [], #We don't want to change any parameters
    "mo_file"               : piecewiseMod_SysDyn_mo_path, # mo file with tabular modified (to allow out of tabular interpolation)
    "plot_std_run"          : False, #Choose to plot std run alognside this test results
    }
    setUpSweepsAndRun(**run_kwargs)

def setUpSweepsAndRun(sweep_params_settings_list,fixed_params,plot_vars,stopTime,scens_to_run,mo_file,plot_std_run,fixed_params_description_str=False):
    startTime = 1900 # year to start the simulation. Because W3-Mod needs the starttime to be always 1900, we don't allow the user to change it
    #The "root" output folder path.
    output_root_path = files_aux.makeOutputPath("modelica_multiparam_sweep")
    #Create scenarios from factory
    scenarios = []
    for scen_num in scens_to_run:
        folder_name = "scenario_"+str(scen_num)
        logger.info("Running scenario {folder_name}".format(folder_name=folder_name))
        # Create main folder
        scen_folder_path = os.path.join(output_root_path,folder_name)
        os.makedirs(scen_folder_path)
        # Create run folder
        run_folder_path  = os.path.join(scen_folder_path,"run")
        os.makedirs(run_folder_path)
        # Write 2 copies of the output mos_path: one in the root folder of the scenario and the other inside the 'run' folder. The second one will be the one being executed.
        output_mos_copy_path = os.path.join(scen_folder_path,gral_settings.mos_script_filename)
        output_mos_tobeExe_path = os.path.join(run_folder_path,gral_settings.mos_script_filename)
        model_name = world3_settings._world3_scenario_model_skeleton.format(scen_num=scen_num)
        multiparamMosWriter = mos_writer.sweeping_mos_writer.MultiparamSweepingMosWriter()
        multiparamMosWriter.createMos(model_name, startTime, stopTime, mo_file, sweep_params_settings_list, fixed_params, output_mos_tobeExe_path, world3_settings.sweeping_csv_file_name_modelica_skeleton,mos_copy_path=output_mos_copy_path)
        # Write run settings:
        run_settings = {
            "sweep_params_settings_list": sweep_params_settings_list,
            "fixed_params": fixed_params,
            "plot_vars": plot_vars,
            "stopTime": stopTime,
            "scen_num": scen_num,
            "model_name": model_name,
            "mo_file": mo_file,
            "plot_std_run": plot_std_run,
            "fixed_params_description_str":fixed_params_description_str,
        }
        writeRunLog(run_settings, os.path.join(scen_folder_path,gral_settings.omc_creation_settings_filename))
        # Run
        running.run_omc.runMosScript(output_mos_tobeExe_path)
        # Get iterations info per param per iteration
        iterationsInfo_list = iterationsInfoForThisRun(sweep_params_settings_list,run_folder_path)
        # Plot desired variables
        plots_folder_path =os.path.join(scen_folder_path,"plots")
        os.makedirs(plots_folder_path)
        # If the fixed params description has not been set (if there are a lot of params changed fixed then a custom description may be advantageous) then make the default one
        if not fixed_params_description_str:
            # If there are no fixed params for this run then just write "None" or similar
            if len(fixed_params) == 0:
                fixed_params_description_str = "None"
            # If there is at least one fixed param, write them separated by commas.
            else:
                fixed_params_description_str = ", ".join([str(x) for x in fixed_params])
        plot_csv.plotVarsFromIterationsInfo(plot_vars,model_name,iterationsInfo_list,plots_folder_path,plot_std_run,fixed_params_description_str)
        # Write automatic readme (with general info and specific info for this sweep)
        readme_path = os.path.join(scen_folder_path,gral_settings.readme_filename)
        readme_writer.writeReadmeMultiparam(readme_path,iterationsInfo_list)

    # setUpSweepsAndRun(**kwargs)
def iterationsInfoForThisRun(sweep_params_settings_list,run_folder_path):
    # We iterate the params in the same order in which they will be iteratted in the fors in the .mos script.
    # For each "total" iteration, each parameter will have it's own "i" set in a value and from that personal "i" and their formula they will calculate their value for the simulation corresponding to this run
    # Here, we will calculate each of those values but in python instead of in Modelica
#     iterationInfo():
# import  simulationParamInfo():
    itersTotal = functools.reduce(lambda accum,e: accum*e, [e.iterations for e in sweep_params_settings_list], 1)

    iterationsInfo_list = []

    counter = [0] * len(sweep_params_settings_list)   # for each param, we keep a count of its internal iterator in this list
    for i_total in range(itersTotal):
        # Calculate the info of each parameter for this iteration
        iterInfo = sweeping.iterationInfo.IterationInfo(i_total, sweep_params_settings_list, counter,run_folder_path)

        # Add 1 to the last param
        counter[len(counter)-1] = counter[len(counter)-1] +1
        # Check if the last params and its predecessors reached their max ( max = #iterations)
        pos = len(counter) -1
        while(counter[pos] == sweep_params_settings_list[pos].iterations and pos > 0):
            counter[pos] = 0   # restart the counter for current pos
            pos = pos -1       # go to previous pos
            counter[pos] = counter[pos] +1    # add 1 to previous pos
        iterationsInfo_list.append(iterInfo)
    return iterationsInfo_list



def writeRunLog(run_settings_dict, output_path):
    intro_str = """The whole "create mos, run it and plot it" script was run with the following settings"""+"\n"
    format_explanation_str = """<setting_name>:\n   <setting_value>"""+"\n"
    all_settings = []
    for setting_name,setting_value in run_settings_dict.items():
        setting_str = """{setting_name}:\n {setting_value}""".format(setting_name=setting_name,setting_value=str(setting_value))
        all_settings.append(setting_str)
    all_settings_str = "\n".join(all_settings)
    final_str = intro_str + format_explanation_str + "\n" + all_settings_str
    files_aux.writeStrToFile(final_str,output_path)
    return 0
def initialFactoryForWorld3ScenarioMultiparamSweep(scen_num,stop_time,mo_file,sweep_params_settings_list,fixed_params=[]):
    #Get the mos script factory for a scenario number (valid from 1 to 11)
    model_name = world3_settings._world3_scenario_model_skeleton.format(scen_num=scen_num) #global
    initial_factory_dict = {
        "model_name"                 : model_name,
        "startTime"                  : 1900, # year to start the simulation. Because W3-Mod needs the starttime to be always 1900, we don't allow the user to change it
        "stopTime"                   : stop_time,
        "mo_file"                    : mo_file,
        "sweep_params_settings_list" : sweep_params_settings_list,
        "fixed_params"               : fixed_params,
        }
    initial_factory = mos_writer.mos_script_factory.MultiparamMosScriptFactory(settings_dict=initial_factory_dict)
    return initial_factory

# FIRST EXECUTABLE CODE:
if __name__ == "__main__":
    main()


#######    BORRAR DE ACA PARA ABAJO:  #######

# Mine:
import mos_writer.mos_script_factory as mos_script_factory
import sweeping.run_and_plot_model as run_and_plot_model
import filesystem.files_aux as files_aux
import settings.settings_world3_sweep as world3_settings
import world3_specific.standard_run_params_defaults
import world3_specific.params_perturber

#Aux for GLOBALS:
## Skeletons of sweep_value_formula_str. Free variable: i (goes from 0 to (iterations-1) ):
_increasing_by_increment_from_initial_skeleton = "{initial} + i*{increment}"
_increasing_by_percentage_from_initial_skeleton = "{initial}*({percentage}/100*i+1)"
def deltaBeforeAndAfter(p,iterations,delta): #Have to create a function for "delta_before_and_after" because I have to convert to int in python and not in the Modelica Scripting Language
    iterations_div_2_int = int(iterations/2)
    return "{p}*(1-{iterations_div_2_int}*{delta}) + {p}*({delta}*i)".format(p=p,iterations_div_2_int=iterations_div_2_int,delta=delta)
## Examples:
# sweep_value_formula_str = _increasing_by_increment_from_initial_skeleton.format(initial=2012,increment=10) # "2012 + i*10" --> 2012,2022,2032...
# sweep_value_formula_str = _increasing_by_percentage_from_initial_skeleton.format(initial=1e12,percentage=20) # "1e12*((20/100)*i+1)" --> 1e12, 1.2e12, 1.4e12 ...
# sweep_value_formula_str = deltaBeforeAndAfter(p=10,delta=0.01,iterations=7) # '10*(1-3*0.01) + 10*(0.01*i)' --> 9.7, 9.8, 9.9, 10, 10.1, 10.2, 10.3
# Special sweeps constants definitions: DON'T CHANGE ANYTHING
SPECIAL_policy_years = None # Special vars sweeping that sweeps the year to apply the different policies respective of each scenario. (each scenario has it's policies to apply.)
# System Dynamics .mo to use:

def main():
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
#### WORK PACKAGE 1 ####
    # testPolicyYears()
    # testDeltaNRResources()
    # testFertility2()
    standardRun(vanilla_SysDyn_mo_path)
    standardRun(piecewiseMod_SysDyn_mo_path)
    standardRun(populationTankNewVar_SysDyn_mo_path)
# The vermeulen tests need a modified SystemDynamics .mo!
    # testVermeulenAndJonghRun2() #Run1 is Meadows' std run
    # testVermeulenAndJonghRun3()
# From IDA sens analysis:
    # testDeltaIncomeExpectAvgTime()
    # testDeltaHlthServImpactDel()
    # testDeltaFrCapAlObtRes2Bracket5Bracket()
  # Tests for 1901 sens
    # testDeltaIndMtlEmissFact()
    # testDeltaAvgLifeIndCap1()
    # testDeltaMtlToxicIndex()
  # MULTI TEST: Multiple tests in one.
    # testMultiTest1901Top20ParamVar()
  # Dynamics to Growth tests:
    # testDeltaICOR()
    # testDeltaPseudoFFWParam()
#### Temp ####
    # testHugoScolnikRuns()
#### WORK PACKAGE 2 ####
    # None. The "sweeps" for empirical sensitivity analysis needed to be different, so we included them in "w3_sens_calculator.py"

## Predefined tests
def testDeltaPseudoFFWParam():
    # Added a parameter called "pseudo_ffw_param" to Scenario_1, Population_Dynamics and
    # BIrths_factors. It's used in Births_factors to calculate the birth rate using the formula of
    # World3-v01 instead of World3-v03 (equivalent to W3-Mod)

    iterations = 10;
    kwargs = {
    "plot_vars":["population"],
    "startTime": 1900 ,# year to start the simulation (1900 example)
    "stopTime": 2500  ,# year to end the simulation (2100 for example)
    "scens_to_run" : [1], #The standard run corresponds to the first scenario
    "iterations" : iterations,
    "sweep_vars":  ["pseudo_ffw_param"], # Examples: SPECIAL_policy_years, ["nr_resources_init"]
    "sweep_value_formula_str" : deltaBeforeAndAfter(p=0.22,delta=0.02,iterations=iterations), # Sweep floor(iterations/2) times before and after p changing by a percentage of delta*100
    "fixed_params" : [],  # No fixed parameter changes. Example: [("nr_resources_init",6.3e9),("des_compl_fam_size_norm",2),...]
    "mo_file" : pseudoffwparam_SysDyn_mo_path, # mo that has pseudo_ffw_param as param
    "plot_std_run": True, #Choose to plot std run alognside this test results
    }
    setUpSweepsAndRun(**kwargs)

def testDeltaICOR():
    ## According to Dynamics To Growth:
    # Run 3-3 (Figure 3-39) DECREASED ICOR BY 33%: ICOR1=2
    # Run 3-4 (Figure 3-40) INCREASED ICOR BY 33%: ICOR1=4
    # ICOR is also modified in Vermeulen but not at the start (in Verm is modified in 1975)
    #   and this is a sweep of only this var
    # ICOR is "p_ind_cap_out_ratio_1", Default: ICOR=3
    # Plots:
    #      "industrial output"                                   --> output Real industrial_output(unit = "dollar/yr") "Total annual world industrial output";
    #      "service output per capita"                           --> output Real serv_out_pc(unit = "dollar/yr") "Total annual services per person";
    #      "capital utilization fraction"                        --> Industrial_Investment1.Industrial_Output.capital_util_fr (there's no var at the top)
    #      "industrial output per capita"                        --> output Real ind_out_pc(unit = "dollar/yr") "Total annual consumer goods per person";
    #      "fraction of industrial output allocated to services" --> output Real s_fioa_serv "Fraction of industrial output allocated to service sector";

    iterations = 9;
    kwargs = {
    "plot_vars":["Industrial_Investment1Industrial_Outputcapital_util_fr"],
    # "plot_vars":["Industrial_Investment1Industrial_Outputcapital_util_fr", "industrial_output", "serv_out_pc", "ind_out_pc", "s_fioa_serv",],
    "startTime": 1900 ,# year to start the simulation (1900 example)
    "stopTime": 2000  ,# year to end the simulation (2100 for example)
    "scens_to_run" : [1], #The standard run corresponds to the first scenario
    "iterations" : iterations,
    "sweep_vars":  ["p_ind_cap_out_ratio_1"], # Examples: SPECIAL_policy_years, ["nr_resources_init"]
    "sweep_value_formula_str" : deltaBeforeAndAfter(p=3,delta=1/12,iterations=iterations), # Sweep floor(iterations/2) times before and after p changing by a percentage of delta*100
    "fixed_params" : [],  # No fixed parameter changes. Example: [("nr_resources_init",6.3e9),("des_compl_fam_size_norm",2),...]
    # "mo_file" : vanilla_SysDyn_mo_path, # Mo without modifications
    "mo_file" : piecewiseMod_SysDyn_mo_path, # mo that interpolates outwards with values that lie outside of range
    "plot_std_run": False, #Choose to plot std run alognside this test results
    }
    setUpSweepsAndRun(**kwargs)

def testMultiTest1901Top20ParamVar():
    # The plot vars remain the same for each sub-test
    # Only one parameter per sub-test (iterating one by one "parameters to sweep" list)
    # SLOWWWWWWW!. Compiles model again for each new param. It was made quickly.
    param_list= \
       [("p_fr_cap_al_obt_res_2[4]" ,0.05 ),
        ("p_avg_life_ind_cap_1"      ,14   ),
        ("ind_mtl_toxic_index"       ,10   ),
        ("p_fr_cap_al_obt_res_2[3]"  ,0.1  ),
        ("p_avg_life_agr_inp_2"      ,2    ),
        ("ind_mtl_emiss_fact"        ,0.1  ),
        ("agr_mtl_toxic_index"       ,1    ),
        ("assim_half_life_1970"      ,1.5  ),
        ("life_expect_norm"          ,28   ),]

    # Common "test arguments":
    kwargs = {
    "plot_vars":["Food_Production1Agr_InpIntegrator1y","Arable_Land_Dynamics1Pot_Arable_LandIntegrator1y","Arable_Land_Dynamics1Arable_LandIntegrator1y","population","nr_resources"],
    "startTime": 1900 ,# year to start the simulation (1900 example)
    "stopTime": 2100  ,# year to end the simulation (2100 for example)
    "scens_to_run" : [1], #The standard run corresponds to the first scenario
    "iterations" : 5,
    "fixed_params" : [],  # No fixed parameter changes. Example: [("nr_resources_init",6.3e9),("des_compl_fam_size_norm",2),...]
    # "mo_file" : vanilla_SysDyn_mo_path, # Mo without modifications
    "mo_file" : piecewiseMod_SysDyn_mo_path, # mo that interpolates outwards with values that lie outside of range
    "plot_std_run": False, #Choose to plot std run alognside this test results
    }
    # Iterate params and run Scenario 1 with ^ settings for each one
    for param,default in param_list:
        kwargs["sweep_vars"] = [param]
        kwargs["sweep_value_formula_str"] = deltaBeforeAndAfter(p=default,delta=0.1,iterations=kwargs["iterations"]) # Sweep floor(iterations/2) times before and after p changing by a percentage of delta*100
        setUpSweepsAndRun(**kwargs)
def testVermeulenAndJonghRun2():
    ### Changes must be made in the code and not in initial parameters
       #Changes for 1975 in the code: (AND NOT IN YEAR 1900)
            # ("p_ind_cap_out_ratio_1",3.3),   #V&J-2: ICOR= 3.3, Default: ICOR=3
            # ("p_fioa_cons_const_1",0.473),   #V&J-2: FIOAC= 0.473, Default: FIOAC=0.43
            # ("p_avg_life_ind_cap_1", 12.6),  #V&J-2: ALIC= 12.6, Default: ALIC=14
    kwargs = {
    "plot_vars":[#"pseudo" parameters:
                 "Industrial_Investment1Industrial_Outputs_ind_cap_out_ratio", "Industrial_Investment1S_FIOA_Conss_fioa_cons_const","Industrial_Investment1S_Avg_Life_Ind_Caps_avg_life_ind_cap",
                 "population","ppoll_index","industrial_output","nr_resources"],#,"nr_resources","Population_Dynamics1FFW"] #without the "." in "...Dynamics.FFW" because numpy doesn't play well with dots in column names
    "startTime": 1900 ,# year to start the simulation (1900 example)
    "stopTime": 2100  ,# year to end the simulation (2100 for example)
    "scens_to_run" : [1] ,#List of ints representing the scenarios to run (from 1 to 11).  Example: [1,2,3,4,5,6,7,8,9]
    "iterations" : 1 ,#No sweeping: more than one iteration is irrelevant
    "sweep_vars": [] ,#No sweeping done in VermeulenAndJonghRun
    "sweep_value_formula_str" : "i" ,#irrelevant formula (no sweeping)
    "fixed_params" : [ ], #No changes in params (for year 1900)
    "mo_file" : Run2vermeulenAndJongh_SysDyn_mo_path,
    "plot_std_run": True, #Choose to plot std run alognside this test results
    }

    setUpSweepsAndRun(**kwargs)
def testVermeulenAndJonghRun3():
    ### Changes must be made in the code and not in initial parameters
       #Changes for 1975 in the code: (AND NOT IN YEAR 1900)
            # ("p_ind_cap_out_ratio_1",2.7),   #V&J-3: ICOR= 2.7, Default: ICOR=3
            # ("p_fioa_cons_const_1",0.387),   #V&J-3: FIOAC= 0.387, Default: FIOAC=0.43
            # ("p_avg_life_ind_cap_1", 15.4),  #V&J-3: ALIC= 15.4, Default: ALIC=14
    kwargs = {
    "plot_vars":[#"pseudo" parameters:
                 "Industrial_Investment1Industrial_Outputs_ind_cap_out_ratio", "Industrial_Investment1S_FIOA_Conss_fioa_cons_const","Industrial_Investment1S_Avg_Life_Ind_Caps_avg_life_ind_cap",
                 "population","ppoll_index","industrial_output","nr_resources"],#,"nr_resources","Population_Dynamics1FFW"] #without the "." in "...Dynamics.FFW" because numpy doesn't play well with dots in column names
    "startTime": 1900 ,# year to start the simulation (1900 example)
    "stopTime": 2100  ,# year to end the simulation (2100 for example)
    "scens_to_run" : [1] ,#List of ints representing the scenarios to run (from 1 to 11).  Example: [1,2,3,4,5,6,7,8,9]
    "iterations" : 1 ,#No sweeping: more than one iteration is irrelevant
    "sweep_vars": [] ,#No sweeping done in VermeulenAndJonghRun
    "sweep_value_formula_str" : "i" ,#irrelevant formula (no sweeping)
    "fixed_params" : [ ], #No changes in params (for year 1900)
    "mo_file" : Run3vermeulenAndJongh_SysDyn_mo_path,
    "plot_std_run": True, #Choose to plot std run alognside this test results
    }

    setUpSweepsAndRun(**kwargs)

def standardRun(mo_file): #ONLY TO GET THE STANDARD CSV!
    kwargs = {
    "plot_vars":["population"],
    "startTime": 1900 ,# year to start the simulation (1900 example)
    "stopTime": 2500  ,# year to end the simulation (2100 for example)
    "scens_to_run" : [1], #The standard run corresponds to the first scenario
    "iterations" : 1, #More than one iteration is irrelevant
    "sweep_vars": [] ,#No sweeping done in std run
    "sweep_value_formula_str" : "i" ,#irrelevant formula (no sweeping)
    "fixed_params" : [], #We don't want to change any parameters
    "mo_file" : mo_file,
    "plot_std_run": False, #Choose to plot std run alognside this test results
    }
    setUpSweepsAndRun(**kwargs)

def testFertility2():
    kwargs = {
    "plot_vars":[],
    "startTime": 1900 ,# year to start the simulation (1900 example)
    "stopTime": 2100  ,# year to end the simulation (2100 for example)
    "scens_to_run" : [1], #The standard run corresponds to the first scenario
    "iterations" : 8, #More than one iteration is irrelevant
    "sweep_vars":  ["pseudo_ffw"], #NOT ORIGINAL PARAMETER! ADDED ONLY TO SCENARIO 1
    "sweep_value_formula_str" : deltaBeforeAndAfter(p=1,delta=0.01,iterations=iterations), #Has to be a string with only free variable "i"
    "fixed_params" : [
            ("p_ind_cap_out_ratio_1",3.15),   #Hugo: ICOR= 3.15, Default: ICOR=3
            ("p_avg_life_ind_cap_1", 13.3),   #Hugo: ALIC= 13.3, Default: ALIC=14
            ("p_avg_life_serv_cap_1", 17.1),  #Hugo: ALSC= 17.1, Default: ALSC=20
            ("p_serv_cap_out_ratio_1", 1.05)  #Hugo: SCOR= 1.05, Default: SCOR=1
        ],
    "mo_file" : vanilla_SysDyn_mo_path, # Mo without modifications
    "plot_std_run": False, #Choose to plot std run alognside this test results
    }
    setUpSweepsAndRun(**kwargs)

def testHugoScolnikRuns():
# Hugo Scolnik article: "Crítica metodológica al modelo WORLD 3" (Methodological criticisim to the World3 model)
#   Perturbed 5 params by 5%
      # ICOR= 3.15, Default: ICOR=3
      # ALIC= 13.3, Default: ALIC=14
      # ALSC= 17.1, Default: ALSC=20
      # SCOR= 1.05, Default: SCOR=1
      # Run "Perturbed": FFW= 0.231, Default: FFW=0.22
      # Run "Perturbed Increasing FFW": FFW= 0.242, Default: FFW=0.22
#   Perturbed rest of the params by a scalar of 0.24172080E-12
# This function:
#   Perturbed 4 params by 5%: (not FFW)
      # ICOR= 3.15, Default: ICOR=3
      # ALIC= 13.3, Default: ALIC=14
      # ALSC= 17.1, Default: ALSC=20
      # SCOR= 1.05, Default: SCOR=1
#   Perturbed rest of the params by a scalar of 0.24172080E-12 (not including FFW)
#   We use a modified W3 version that replaces the births function from W3-v03 (corresponding to W3-Modelica) with the "old" births function from W3-v01 that included the parameter ffw. We call it "pseudo_ffw_param".
#   Swept pseudo_ffw_param by 10% up and down with a granularity of 2% to include both Runs from paper in same plot
    perturbing_scalar = 0.24172080E-12
    percentage_to_perturb = perturbing_scalar*100

    # Get full list of params
    default_params_info_list   = world3_specific.standard_run_params_defaults.w3_params_info_list
    # set 4 params perturbed values manually
    special_params = ["pseudo_ffw_param","p_ind_cap_out_ratio_1", "p_avg_life_ind_cap_1", "p_avg_life_serv_cap_1", "p_serv_cap_out_ratio_1",]
    special_params_perturbed_info_list = [
       ("p_ind_cap_out_ratio_1",3.15),   #Hugo: ICOR= 3.15, Default: ICOR=3
       ("p_avg_life_ind_cap_1", 13.3),   #Hugo: ALIC= 13.3, Default: ALIC=14
       ("p_avg_life_serv_cap_1", 17.1),  #Hugo: ALSC= 17.1, Default: ALSC=20
       ("p_serv_cap_out_ratio_1", 1.05),  #Hugo: SCOR= 1.05, Default: SCOR=1
        ]
    #   remove 5 params from list
    rest_of_params = [x[0] for x in default_params_info_list if x[0] not in special_params]
    # set rest of params perturbed values by adding a scalar
    rest_of_params_perturbed_info_list = world3_specific.params_perturber.perturbeParameterByPercentage(rest_of_params,percentage_to_perturb)
    fixed_params = special_params_perturbed_info_list + rest_of_params_perturbed_info_list
    iterations = 11
    kwargs = {
    "plot_vars":["population"],
    "startTime": 1900 ,# year to start the simulation (1900 example)
    "stopTime": 2300  ,# year to end the simulation (2100 for example)
    "scens_to_run" : [1], #The standard run corresponds to the first scenario
    "iterations" : iterations,
    "sweep_vars":  ["pseudo_ffw_param"], #NOT ORIGINAL PARAMETER! ADDED ONLY TO SCENARIO 1
    "sweep_value_formula_str" : deltaBeforeAndAfter(p=0.22,delta=0.02,iterations=iterations),
    "fixed_params" : fixed_params,
    "mo_file" : pseudoffwparam_SysDyn_mo_path,
    "plot_std_run": True, #Choose to plot std run alognside this test results
    "fixed_params_description_str": "By +5%: \np_ind_cap_out_ratio_1, p_avg_life_ind_cap_1, p_avg_life_serv_cap_1, p_serv_cap_out_ratio_1.\nBy increase of small percentage: \nThe rest.",
    }

    setUpSweepsAndRun(**kwargs)

    ### BORRAR DESDE ACA HASTA EL FIN DE LA FUNCIÓN
    # print(len(default_params_info_list))
    # print(len(special_params_perturbed_info_list))
    # print(len(rest_of_params_perturbed_info_list))
    # print(len(fixed_params))
    # print(fixed_params)

def testDeltaIndMtlEmissFact():
    iterations = 10;
    kwargs = {
    "plot_vars":["Food_Production1Agr_InpIntegrator1y","Arable_Land_Dynamics1Pot_Arable_LandIntegrator1y","Arable_Land_Dynamics1Arable_LandIntegrator1y","population","nr_resources"], # Examples: SPECIAL_policy_years, ["nr_resources_init"]
    "startTime": 1900 ,# year to start the simulation (1900 example)
    "stopTime": 1910  ,# year to end the simulation (2100 for example)
    "scens_to_run" : [1], #The standard run corresponds to the first scenario
    "iterations" : iterations,
    "sweep_vars":  ["ind_mtl_emiss_fact"], # Examples: SPECIAL_policy_years, ["nr_resources_init"]
    "sweep_value_formula_str" : deltaBeforeAndAfter(p=0.1,delta=0.1,iterations=iterations), # Sweep floor(iterations/2) times before and after p changing by a percentage of delta*100
    "fixed_params" : [],  # No fixed parameter changes. Example: [("nr_resources_init",6.3e9),("des_compl_fam_size_norm",2),...]
    "mo_file" : vanilla_SysDyn_mo_path, # Mo without modifications
    "plot_std_run": False, #Choose to plot std run alognside this test results
    }
    setUpSweepsAndRun(**kwargs)
def testDeltaFrCapAlObtRes2Bracket4Bracket():
    iterations = 10;
    kwargs = {
    "plot_vars":["Food_Production1Agr_InpIntegrator1y","population" "Arable_Land_Dynamics1Arable_LandIntegrator1y", "Arable_Land_Dynamics1Pot_Arable_LandIntegrator1y"],
    "startTime": 1900 ,# year to start the simulation (1900 example)
    "stopTime": 2100  ,# year to end the simulation (2100 for example)
    "scens_to_run" : [1], #The standard run corresponds to the first scenario
    "iterations" : iterations,
    "sweep_vars":  ["p_fr_cap_al_obt_res_2[4]"], # Examples: SPECIAL_policy_years, ["nr_resources_init"]
    "sweep_value_formula_str" : deltaBeforeAndAfter(p=0.05,delta=0.1,iterations=iterations), # Sweep floor(iterations/2) times before and after p changing by a percentage of delta*100
    "fixed_params" : [],  # No fixed parameter changes. Example: [("nr_resources_init",6.3e9),("des_compl_fam_size_norm",2),...]
    "mo_file" : vanilla_SysDyn_mo_path, # Mo without modifications
    "plot_std_run": False, #Choose to plot std run alognside this test results
    }
    setUpSweepsAndRun(**kwargs)
def testDeltaFrCapAlObtRes2Bracket5Bracket():
    iterations = 10;
    kwargs = {
    "plot_vars":["Food_Production1Agr_InpIntegrator1y","population"],
    "startTime": 1900 ,# year to start the simulation (1900 example)
    "stopTime": 2100  ,# year to end the simulation (2100 for example)
    "scens_to_run" : [1], #The standard run corresponds to the first scenario
    "iterations" : iterations,
    "sweep_vars":  ["p_fr_cap_al_obt_res_2[5]"], # Examples: SPECIAL_policy_years, ["nr_resources_init"]
    "sweep_value_formula_str" : deltaBeforeAndAfter(p=0.05,delta=0.1,iterations=iterations), # Sweep floor(iterations/2) times before and after p changing by a percentage of delta*100
    "fixed_params" : [],  # No fixed parameter changes. Example: [("nr_resources_init",6.3e9),("des_compl_fam_size_norm",2),...]
    "mo_file" : vanilla_SysDyn_mo_path, # Mo without modifications
    "plot_std_run": False, #Choose to plot std run alognside this test results
    }
    setUpSweepsAndRun(**kwargs)
def testDeltaHlthServImpactDel():
    iterations = 5;
    kwargs = {
    "plot_vars":["Food_Production1Agr_InpIntegrator1y","population"],
    "startTime": 1900 ,# year to start the simulation (1900 example)
    "stopTime": 2100  ,# year to end the simulation (2100 for example)
    "scens_to_run" : [1], #The standard run corresponds to the first scenario
    "iterations" : iterations,
    "sweep_vars":  ["hlth_serv_impact_del"], # Examples: SPECIAL_policy_years, ["nr_resources_init"]
    "sweep_value_formula_str" : deltaBeforeAndAfter(p=20,delta=0.1,iterations=iterations), # Sweep floor(iterations/2) times before and after p changing by a percentage of delta*100
    "fixed_params" : [],  # No fixed parameter changes. Example: [("nr_resources_init",6.3e9),("des_compl_fam_size_norm",2),...]
    "mo_file" : vanilla_SysDyn_mo_path, # Mo without modifications
    "plot_std_run": False, #Choose to plot std run alognside this test results
    }
    setUpSweepsAndRun(**kwargs)
def testDeltaIncomeExpectAvgTime():
    iterations = 10;
    kwargs = {
    "plot_vars":["Food_Production1Agr_InpIntegrator1y","Population_Dynamics1Pop_0_14y","population"],
    "startTime": 1900 ,# year to start the simulation (1900 example)
    "stopTime": 2100  ,# year to end the simulation (2100 for example)
    "scens_to_run" : [1], #The standard run corresponds to the first scenario
    "iterations" : iterations,
    "sweep_vars":  ["income_expect_avg_time"], # Examples: SPECIAL_policy_years, ["nr_resources_init"]
    "sweep_value_formula_str" : deltaBeforeAndAfter(p=3,delta=0.1,iterations=iterations), # Sweep floor(iterations/2) times before and after p changing by a percentage of delta*100
    "fixed_params" : [],  # No fixed parameter changes. Example: [("nr_resources_init",6.3e9),("des_compl_fam_size_norm",2),...]
    "mo_file" : vanilla_SysDyn_mo_path, # Mo without modifications
    "plot_std_run": False, #Choose to plot std run alognside this test results
    }
    setUpSweepsAndRun(**kwargs)
def testDeltaMtlToxicIndex():
    iterations = 5;
    kwargs = {
    "plot_vars":["Food_Production1Agr_InpIntegrator1y","Arable_Land_Dynamics1Pot_Arable_LandIntegrator1y","Arable_Land_Dynamics1.Arable_Land.Integrator1.y","population","nr_resources"],
    "startTime": 1900 ,# year to start the simulation (1900 example)
    "stopTime": 1910  ,# year to end the simulation (2100 for example)
    "scens_to_run" : [1], #The standard run corresponds to the first scenario
    "iterations" : iterations,
    "sweep_vars":  ["ind_mtl_toxic_index"], # Examples: SPECIAL_policy_years, ["nr_resources_init"]
    "sweep_value_formula_str" : deltaBeforeAndAfter(p=10,delta=0.1,iterations=iterations), # Sweep floor(iterations/2) times before and after p changing by a percentage of delta*100
    "fixed_params" : [],  # No fixed parameter changes. Example: [("nr_resources_init",6.3e9),("des_compl_fam_size_norm",2),...]
    "mo_file" : vanilla_SysDyn_mo_path, # Mo without modifications
    "plot_std_run": False, #Choose to plot std run alognside this test results
    }
    setUpSweepsAndRun(**kwargs)
def testDeltaAvgLifeIndCap1():
    iterations = 5;
    kwargs = {
    "plot_vars":["Food_Production1Agr_InpIntegrator1y","Arable_Land_Dynamics1Pot_Arable_LandIntegrator1y","Arable_Land_Dynamics1.Arable_Land.Integrator1.y","population","nr_resources"],
    "startTime": 1900 ,# year to start the simulation (1900 example)
    "stopTime": 1910  ,# year to end the simulation (2100 for example)
    "scens_to_run" : [1], #The standard run corresponds to the first scenario
    "iterations" : iterations,
    "sweep_vars":  ["p_avg_life_ind_cap_1"], # Examples: SPECIAL_policy_years, ["nr_resources_init"]
    "sweep_value_formula_str" : deltaBeforeAndAfter(p=14,delta=0.1,iterations=iterations), # Sweep floor(iterations/2) times before and after p changing by a percentage of delta*100
    "fixed_params" : [],  # No fixed parameter changes. Example: [("nr_resources_init",6.3e9),("des_compl_fam_size_norm",2),...]
    "mo_file" : vanilla_SysDyn_mo_path, # Mo without modifications
    "plot_std_run": False, #Choose to plot std run alognside this test results
    }
    setUpSweepsAndRun(**kwargs)
def testDeltaNRResources():
    kwargs = {
    "plot_vars":[],
    "startTime": 1900 ,# year to start the simulation (1900 example)
    "stopTime": 2100  ,# year to end the simulation (2100 for example)
    "scens_to_run" : [1], #The standard run corresponds to the first scenario
    "iterations" : 10,
    "sweep_vars":  ["nr_resources_init"], # Sweep only one var: "nr_resources_init". Examples: SPECIAL_policy_years, ["nr_resources_init"]
    "sweep_value_formula_str" : deltaBeforeAndAfter(p=1e12,delta=0.1,iterations=iterations), # Sweep floor(iterations/2) times before and after p changing by a percentage of delta*100
    "fixed_params" : [],  # No fixed parameter changes. Example: [("nr_resources_init",6.3e9),("des_compl_fam_size_norm",2),...]
    "mo_file" : vanilla_SysDyn_mo_path, # Mo without modifications
    "plot_std_run": False, #Choose to plot std run alognside this test results
    }
    setUpSweepsAndRun(**kwargs)

def testPolicyYears():
    kwargs = {
    "plot_vars":["population","nr_resources"],
    "startTime": 1900 ,# year to start the simulation (1900 example)
    "stopTime": 2200  ,# year to end the simulation (2100 for example)
    "scens_to_run" : [9],
    "iterations" : 1,
    "sweep_vars":  SPECIAL_policy_years, # Set to SPECIAL_policy_years to use scenario specific defaults (year of application of policies). Examples: SPECIAL_policy_years, ["nr_resources_init"]
    "sweep_value_formula_str" : _increasing_by_increment_from_initial_skeleton.format(initial=2022,increment=10), # "2012 + i*10" --> 2012,2022,2032...
    "fixed_params" : [],  # No fixed parameter changes. Example: [("nr_resources_init",6.3e9),("des_compl_fam_size_norm",2),...]
    "mo_file" : vanilla_SysDyn_mo_path, # Mo without modifications
    "plot_std_run": False, #Choose to plot std run alognside this test results
    }
    setUpSweepsAndRun(**kwargs)

#World3 specific:
def setUpSweepsAndRun(iterations,sweep_vars,sweep_value_formula_str,fixed_params,plot_vars,startTime,stopTime,scens_to_run,mo_file,plot_std_run=False,fixed_params_description_str=False):
    #The "root" output folder path.
    output_path = files_aux.makeOutputPath()
    #Create scenarios from factory
    scenarios = []
    for i in scens_to_run:
        initial_factory_for_scen_i = initialFactoryForWorld3Scenario(scen_num=i,start_time=startTime,stop_time=stopTime,mo_file=mo_file,fixed_params=fixed_params,sweep_vars=sweep_vars)
        scenario_tuple =("scenario_"+str(i),initial_factory_for_scen_i)
        scenarios.append(scenario_tuple)
    doScenariosSet(scenarios, plot_vars=plot_vars,iterations=iterations,output_root_path=output_path, sweep_value_formula_str=sweep_value_formula_str,plot_std_run=plot_std_run,fixed_params_description_str=fixed_params_description_str)
def doScenariosSet(scenarios,plot_vars,iterations,output_root_path,sweep_value_formula_str,plot_std_run,fixed_params_description_str):
    for folder_name,initial_scen_factory in scenarios:
        logger.info("Running scenario {folder_name}".format(folder_name=folder_name))
        os.makedirs(os.path.join(output_root_path,folder_name))
        run_and_plot_model.createSweepRunAndPlotForModelInfo(initial_scen_factory,plot_vars=plot_vars,iterations=iterations,output_folder_path=os.path.join(output_root_path,folder_name),sweep_value_formula_str=sweep_value_formula_str,csv_file_name_modelica_skeleton=world3_settings.sweeping_csv_file_name_modelica_skeleton,csv_file_name_python_skeleton=world3_settings.sweeping_csv_file_name_python_skeleton,plot_std_run=plot_std_run,fixed_params_description_str=fixed_params_description_str)
def defaultSweepVarsForScenario(scen_num):
    default_sweep_vars_dict = defaultSweepVarsDict()
    return default_sweep_vars_dict[scen_num]
def defaultSweepVarsDict():
    default_sweep_vars_dict ={
            9: ["t_fcaor_time", "t_fert_cont_eff_time", "t_zero_pop_grow_time", "t_ind_equil_time", "t_policy_year", "t_land_life_time"],
            8: ["t_fcaor_time", "t_fert_cont_eff_time", "t_zero_pop_grow_time", "t_ind_equil_time", "t_policy_year"],
            7: ["t_fcaor_time", "t_fert_cont_eff_time", "t_zero_pop_grow_time"],
            6: ["t_fcaor_time", "t_policy_year", "t_land_life_time"],
            5: ["t_fcaor_time", "t_policy_year", "t_land_life_time"],
            4: ["t_fcaor_time", "t_policy_year"],
            3: ["t_fcaor_time", "t_policy_year"],
            2: ["t_fcaor_time"],
            1: []
            }
    return default_sweep_vars_dict

