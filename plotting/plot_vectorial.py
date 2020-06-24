import os
import numpy
import pandas
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import logging

import plotting.plot_lines as plot_lines
import plotting.plot_specs as plot_specs

filehandler = logging.FileHandler("/home/omsens/Documents/results_experiments/logging/vectorial_analysis.log")
logger = logging.getLogger("vectorial_analysis")
logger.addHandler(filehandler)
logger.setLevel(logging.DEBUG)


class VectorialPlotter:
    def __init__(self, optim_result, df_x_opt_run, df_x0_run, df_restriction, var_optimization, var_restriction):
        self.optim_result = optim_result

        self.var_optimization = var_optimization
        self.df_x_opt_run = df_x_opt_run

        self.df_x0_run = df_x0_run

        self.var_restriction = var_restriction
        self.df_restriction = df_restriction

        # TODO: IMPORTANT. Check that the columns in df_x_opt_run, df_x0_run and df_restriction are consistent

    def plotInFolder(self, plots_folder_path, extra_ticks=[]):
        # logger.debug("enter plotInFolder")
        file_name_without_extension = self.optim_result.variable_name
        plot_path_without_extension = os.path.join(plots_folder_path, file_name_without_extension)
        # logger.debug("Initialize perturbed run specs")
        lines_specs = [self.perturbedRunSpecs()]
        # Standard
        if self.df_x0_run is not None:
            df = self.df_x0_run
            specs = self.regular_run_line_specs(df, self.var_optimization+'_STD-RUN', self.var_optimization, '-')
            lines_specs.append(specs)
        # Restriction
        if self.df_restriction is not None:
            # ax2 = ax[1].twinx()
            df = self.df_restriction
            specs = self.regular_run_line_specs(df, self.var_restriction+'-restriction', self.var_restriction, '--')
            lines_specs.append(specs)

        # Initialize plot_specs
        logger.debug("Initialize plot_specs")
        setup_specs = self.plotSetupSpecs(extra_ticks)

        vect_plot_specs = plot_specs.PlotSpecs(setup_specs, lines_specs)
        lines_plotter = plot_lines.LinesPlotter(vect_plot_specs)
        lines_plotter.plotInPath(plot_path_without_extension)
        png_plot_path = "{0}.png".format(plot_path_without_extension)
        return png_plot_path

    def perturbedRunSpecs(self):
        # Prepare info
        df         = self.df_x_opt_run
        x_var      = "time"
        y_var      = self.optim_result.variable_name
        linewidth  = 2
        linestyle  = "-"
        markersize = 0
        marker     = 'o'
        label      = self.optim_result.variable_name + "-optimum"
        color      = "red"
        # Initialize plot line specs
        std_run_specs = plot_specs.PlotLineSpecs(
            df         = df,
            x_var      = x_var,
            y_var      = y_var,
            linewidth  = linewidth,
            linestyle  = linestyle,
            markersize = markersize,
            marker     = marker,
            label      = label,
            color      = color
        )
        return std_run_specs

    def regular_run_line_specs(self, df, axis_name, variable_name, linestyle):
        # Prepare info
        x_var      = "time"
        y_var      = variable_name
        linewidth  = 1
        markersize = 0
        marker     = 'o'
        label      = axis_name
        color      = "black"
        # Initialize plot line specs
        std_run_specs = plot_specs.PlotLineSpecs(
           df         = df,
           x_var      = x_var,
           y_var      = y_var,
           linewidth  = linewidth,
           linestyle  = linestyle,
           markersize = markersize,
           marker     = marker,
           label      = label,
           color      = color
        )
        return std_run_specs

    # TODO: add loss of constraint AND loss of objective variable (of course only when constrained is enforced)
    def plotSetupSpecs(self, extra_ticks):
        # Get the info for the plot setup specs
        title    = "Comparison between Standard and Optimum runs"
        subtitle = "variable: {0} = {1}".format(self.optim_result.variable_name,
                                                np.round(self.optim_result.target_optimum, 5))
        footer   = self.footerStr()
        x_label = "Time"
        y_label = ""
        # Initialize the plot setup specs
        setup_specs = plot_specs.PlotSetupSpecs(
            title       = title,
            subtitle    = subtitle,
            footer      = footer,
            x_label     = x_label,
            y_label     = y_label ,
            extra_ticks = extra_ticks
        )
        return setup_specs

    def footerStr(self):
        # Get x_opt to minimize syntax cluttering
        x_opt = self.optim_result.x_opt
        # Define footer first line
        footer_first_line = "Optimum values:"
        # Get strings per params
        params_strs = ["{0}={1:.2f}".format(p_name,p_val) for p_name,p_val in x_opt.items()]
        # Divide the params in chunks to have many short lines in the plot instead of one long one
        group_size = 3
        params_groups_raw_strs = [params_strs[i:i + group_size] for i in range(0, len(params_strs), group_size)]
        params_groups_strs =  [", ".join(group_strs) for group_strs in params_groups_raw_strs]
        # Join all groups strs
        all_params_str = "\n".join(params_groups_strs)
        # Join all lines
        lines = [footer_first_line,all_params_str]
        footer = "\n".join(lines)
        return footer
