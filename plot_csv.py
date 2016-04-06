import logging #en reemplazo de los prints
logger = logging.getLogger("--CSV Plotter--") #un logger especifico para este modulo
import numpy as np
import matplotlib.pyplot as plt
import matplotlib #for configuration


def main():
    #ENTRADA:
    # csvs_list = ["BouncingBall_1_res.csv","BouncingBall_2_res.csv","BouncingBall_3_res.csv"]
    # csvs_list = ["SystemDynamics.WorldDynamics.World3.Scenario_1_1_res.csv","SystemDynamics.WorldDynamics.World3.Scenario_1_2_res.csv"]
    # plot_path = "tmp/plot.svg"
    # var_name = "nr_resources"
    # plot_title = "Ploteo de archivito"
    # # /ENTRADA
    # plotVarFromCSVs(var_name,csvs_list,plot_path, plot_title)


    var_name="population"
    sweeping_info = {'sweep_vars': ['nr_resources_init'], 'per_iter_info_dict': {0: {'file_path':
'/home/adanos/Documents/TPs/tesis/repos/modelica_scripts/tmp/modelica_outputs/2016-04-06/07_52_06/scenario_1/SystemDynamics.WorldDynamics.World3.Scenario_1_0_res.csv',
'sweep_value': 1000000000000.0}, 1: {'file_path':
'/home/adanos/Documents/TPs/tesis/repos/modelica_scripts/tmp/modelica_outputs/2016-04-06/07_52_06/scenario_1/SystemDynamics.WorldDynamics.World3.Scenario_1_1_res.csv',
'sweep_value': 1200000000000.0}, 2: {'file_path':
'/home/adanos/Documents/TPs/tesis/repos/modelica_scripts/tmp/modelica_outputs/2016-04-06/07_52_06/scenario_1/SystemDynamics.WorldDynamics.World3.Scenario_1_2_res.csv',
'sweep_value': 1400000000000.0}, 3: {'file_path':
'/home/adanos/Documents/TPs/tesis/repos/modelica_scripts/tmp/modelica_outputs/2016-04-06/07_52_06/scenario_1/SystemDynamics.WorldDynamics.World3.Scenario_1_3_res.csv',
'sweep_value': 1600000000000.0}, 4: {'file_path':
'/home/adanos/Documents/TPs/tesis/repos/modelica_scripts/tmp/modelica_outputs/2016-04-06/07_52_06/scenario_1/SystemDynamics.WorldDynamics.World3.Scenario_1_4_res.csv',
'sweep_value': 1800000000000.0}, 5: {'file_path':
'/home/adanos/Documents/TPs/tesis/repos/modelica_scripts/tmp/modelica_outputs/2016-04-06/07_52_06/scenario_1/SystemDynamics.WorldDynamics.World3.Scenario_1_5_res.csv',
'sweep_value': 2000000000000.0}}}
    plot_path = "/home/adanos/Documents/TPs/tesis/repos/modelica_scripts/tmp/test.svg"
    plotVarFromSweepingInfo(var_name,sweeping_info,plot_path)
def plotVarFromSweepingInfo(var_name,model_name,sweeping_info,plot_path):
    logger_plot_str = "Plotting:\n  plotvar:{var_name}\n path:{plot_path}".format(var_name=var_name,plot_path=plot_path)
    logger.debug(logger_plot_str)
    title = "Sweeping Plot for model: {model_name}".format(model_name=model_name)
    subtitle ="Plotting var: {var_name}".format(var_name=var_name)
    per_iter_info_dict = sweeping_info["per_iter_info_dict"]
    sweep_vars  = sweeping_info["sweep_vars"]
    sweep_vars_str = ", ".join(sweep_vars)
    footer = "Sweeping variables (all the same value):\n {sweep_vars_str}".format(sweep_vars_str=sweep_vars_str)
    footer_artist = setupPlt("Time","f(x)",title,subtitle,footer)
    per_iter_info_dict = sweeping_info["per_iter_info_dict"]
    iterations = per_iter_info_dict.keys()

    for i in iterations:
        iter_dict = per_iter_info_dict[i]
        file_path = iter_dict["file_path"]
        data = readFromCSV(file_path)
        sweep_value = iter_dict["sweep_value"]
        label = "val={sweep_value}".format(sweep_value=sweep_value)
        plt.plot(data["time"], data[var_name], linewidth=0.5, linestyle='-', markersize=0,marker='o',label=label )
        # plt.legend(loc="best",fontsize="small")
    plt.grid()
    lgd = plt.legend(loc="center left",fontsize="small",fancybox=True, shadow=True, bbox_to_anchor=(1,0.5)) #A la derecha
    # lgd = plt.legend(loc="center left",fontsize="small",fancybox=True, shadow=True, bbox_to_anchor=(0.5,-0.5)) #Abajo (anda mal)
    # saveAndClearPlt(plot_path,lgd)
    saveAndClearPlt(plot_path,lgd,footer_artist)
def plotVarFromCSVs(var_name,csvs_list,plot_path, plot_title):
    # IMPORTANT: needs fix with new setupPlt!!! (doesn't work)
    logger_plot_str = "Plotting:\n  plotvar:{var_name}\n  csvs:{csvs_list}\n path:{plot_path}".format(var_name=var_name,csvs_list=csvs_list,plot_path=plot_path)
    logger.debug(logger_plot_str)
    setupPlt("Time","f(x)",plot_title)

    for file_path in csvs_list:
        data = readFromCSV(file_path)
        file_name= file_path.split("/")[-1] #Creo que no funciona en MS-Win (barra distinta en paths)
        label = "{prefix}_{suffix}".format(prefix=var_name,suffix=file_name)
        plt.plot(data["time"], data[var_name], linewidth=0.5, linestyle='-', markersize=0,marker='o',label=label )
        # plt.legend(loc="best",fontsize="small")
    plt.grid()
    lgd = plt.legend(loc="center left",fontsize="small",fancybox=True, shadow=True, bbox_to_anchor=(1,0.5)) #A la derecha
    # lgd = plt.legend(loc="center left",fontsize="small",fancybox=True, shadow=True, bbox_to_anchor=(0.5,-0.5)) #Abajo (anda mal)
    saveAndClearPlt(plot_path,lgd)


def readFromCSV(file_path):
    data = np.genfromtxt(file_path, delimiter=',', skip_footer=10, names=True)
    return data

def setupPlt(x_label,y_label,title,subtitle,footer):
# def setupPlt(x_label,y_label,title):
    # matplotlib.rcParams.update({'figure.autolayout': True})
    plt.gca().set_position([0.10, 0.15, 0.80, 0.77])
    plt.xlabel(x_label)
    plt.title(title+"\n"+subtitle, fontsize=14)
    # plt.title(title)
    plt.ylabel(y_label)
    footer_artist = plt.annotate(footer, (0,0), (0, -40), xycoords='axes fraction', textcoords='offset points', va='top')
    # fig = plt.figure()
    # fig.text(.1,.1,footer)
    # plt.figtext(.1,.1,footer)
    return footer_artist

def saveAndClearPlt(plot_path,lgd,footer_artist):
    # plt.savefig(plot_path)
    plt.savefig(plot_path,bbox_extra_artists=(lgd,footer_artist), bbox_inches='tight')
    # plt.show()
    plt.clf()

if __name__ == "__main__":
    main()

