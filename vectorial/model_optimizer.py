# Std
import logging
import numpy as np
# Project
import modelica_interface.build_model as build_model
import vectorial.optimization_result as optimization_result
import pandas as pd

from fortran_interface_curvif.curvif_simplified import curvif_simplified as curvif_func
from fortran_interface_curvifgr.curvifgr_simplified import curvifgr_simplified as curvifgr_func

filehandler = logging.FileHandler("/home/omsens/Documents/results_experiments/logging/model_optimizer.log")
logger = logging.getLogger("model_optimizer")
logger.addHandler(filehandler)
logger.setLevel(logging.DEBUG)


class ModelOptimizer:
    def __init__(self, model_name, start_time, stop_time, model_file_path, target_var_name,
                 parameters_to_perturb, max_or_min, build_folder_path,
                 objective_function_name, optimizer_name, alpha_value,
                 constrained_time_path_file, constrained_variable, constrained_epsilon,
                 base_dir, results_dirname):
        logger.debug('Start initilization of ModelOptimizer')

        # Save args
        self.model_name = model_name
        self.start_time = start_time
        self.stop_time = stop_time
        self.model_file_path = model_file_path
        self.target_var_name = target_var_name
        self.parameters_to_perturb = parameters_to_perturb
        self.max_or_min = max_or_min

        self.objective_function_name = objective_function_name
        self.optimizer_name = optimizer_name
        self.alpha_value = alpha_value
        self.constrained_time_path_file = constrained_time_path_file
        self.constrained_variable = constrained_variable
        self.constrained_epsilon = constrained_epsilon

        # Some sanity checks
        # TODO: read possible names for optimizer and objective function from somewhere (config file?)
        if self.optimizer_name not in ['CURVIFGR', 'CURVIF']:
            raise Exception('Error: Optimizer name must be one of CURVIF, CURVIFGR')
        if self.objective_function_name not in ['Alpha weighted path constrained', 'Single variable']:
            raise Exception('Error: Objective function must be one of Alpha weighted, Single variable')

        ###############################
        # Initilization of optimizer
        if self.optimizer_name == 'CURVIFGR':
            self.optimizer = curvifgr_func
        elif self.optimizer_name == 'CURVIF':
            self.optimizer = curvif_func
        else:
            raise Exception('Error: Optimizer name must be one of CURVIF, CURVIFGR')

        # logger.debug('Starting initilization of model_builder')
        model_builder = build_model.ModelicaModelBuilder(model_name, start_time, stop_time, model_file_path)

        logger.debug('Getting compiled model')
        self.compiled_model = model_builder.buildToFolderPath(build_folder_path, base_dir, results_dirname)

        self.x0_dict = {p: self.compiled_model.defaultParameterValue(p) for p in parameters_to_perturb}
        self.x0 = [self.x0_dict[p] for p in parameters_to_perturb]

        ###############################
        # Initialize objective function
        if self.objective_function_name == 'Single variable':
            self.target_var_name_optimum = 1
            self.obj_func = createObjectiveFunctionForModel(self.compiled_model, parameters_to_perturb,
                                                            target_var_name, max_or_min)

        elif self.objective_function_name == 'Alpha weighted path constrained':
            # TODO: allow constrained path to depend on more than one single variable (read by parameter too from OM)
            # logger.debug("Fetching df_origin")
            df_origin = pd.read_csv(constrained_time_path_file, index_col=False)
            # TODO: makes not sense. A warning should be raised to the user
            if self.constrained_variable not in list(df_origin.columns):
                df_origin[self.constrained_variable] = 0

            df_origin = df_origin[['time', self.constrained_variable]].rename(
                columns={self.constrained_variable: 'value'})

            df_actual = pd.read_csv(results_dirname, index_col=False)
            df_actual = df_actual[['time', self.constrained_variable]].rename(
                columns={self.constrained_variable: 'value'})

            self.target_var_name_optimum = df_actual['value'].values[-1]
            self.df_constrained_path = pd.DataFrame(columns=['time_values', 'target_values_constrained_path'])
            self.df_actual_path = pd.DataFrame(columns=['time_values', 'target_values_actual_path'])

            # Get dataframes
            self.df_constrained_path['time_values'] = df_origin['time'].tolist()
            self.df_constrained_path['target_values_constrained_path'] = df_origin['value'].tolist()
            self.df_actual_path['time_values'] = df_actual['time'].tolist()
            self.df_actual_path['target_values_actual_path'] = df_actual['value'].tolist()

            # TODO: separate target_var_name and contrains_var_name
            self.obj_func = createPathConstrainedObjectiveFunctionForModel(self.compiled_model, parameters_to_perturb,
                                                                           target_var_name, max_or_min,
                                                                           self.df_constrained_path.copy(),
                                                                           results_dirname,
                                                                           self.objective_function_name, self.alpha_value)
        else:
            raise Exception('Error')

    def optimize(self, percentage, epsilon):

        logger.debug('Run optimize')

        # Run a standard simulation to have f(x0) before optimizing
        f_x0 = self.compiled_model.quickSimulate(self.target_var_name)

        # Calculate bounds from percentage
        lower_bounds = [x * (1 - percentage / 100) for x in self.x0]
        upper_bounds = [x * (1 + percentage / 100) for x in self.x0]

        # Run the optimizer
        x_opt, f_opt_internal = self.optimizer(self.x0, self.obj_func, lower_bounds, upper_bounds, epsilon)

        # Organize the parameters values in a dict
        x_opt_dict = {self.parameters_to_perturb[i]: x_opt[i] for i in range(len(self.parameters_to_perturb))}

        # If we were maximizing, we have to multiply again by -1
        if self.max_or_min == "max":
            f_opt = -f_opt_internal
        else:
            # If we were minimizing, the internal f(x) will be the final one
            f_opt = f_opt_internal

        # Initialize optimization result object
        optim_result = optimization_result.ModelOptimizationResult(self.x0_dict, x_opt_dict, f_x0, f_opt,
                                                                   self.stop_time,
                                                                   self.target_var_name, self.target_var_name_optimum)

        logger.debug('Run optimize finish')

        # Return optimization result
        return optim_result


# Path Constrained Objective Function
def createPathConstrainedObjectiveFunctionForModel(compiled_model, parameters_to_perturb, target_var_name, max_or_min,
                                                   df_constrained_path, results_dirname, objective_function_name,
                                                   alpha_value):

    if objective_function_name != 'Alpha weighted path constrained':
        raise Exception('Not implemented: right now the only constrained function method is '
                        'Alpha weighted path constrained')

    # TODO: fetch epsilon value in the right way (pass by parameter in OpenModelica)
    # Define Epsilon: allowed difference in time for data points to be considered the same point in loss function
    epsilon_constraint_time = 0.01

    # Loss function definition
    def loss_function_path_trajectory(df_constrained, df_actual_path):
        # Calculation
        # df_times = df_actual_path['time_values'].tolist()
        # def get_nearest_time(row):
        #     t, d, ans = row['time_values'], np.inf, np.nan
        #     for t2 in df_times:
        #         diff = np.abs(t2 - t)
        #         if diff < d:
        #             d = diff
        #             ans = t2
        #         else:
        #             break
        #     return ans if d < epsilon_constraint_time else np.nan
        # # Apply function
        # df_constrained['time_values_nearest'] = df_constrained.apply(get_nearest_time, 1)
        # # Calculate error
        # limits = df_constrained[~df_constrained['time_values_nearest'].isnull()].rename(columns={
        #     'target_values_constrained_path': 'value_target'
        # })
        # # Note: drop duplicates in case the time series is constant for certain time
        # limits = pd.merge(limits, df_actual_path.rename(columns={
        #     'time_values': 'time_values_nearest',
        #     'target_values_actual_path': 'value_real'}),
        #     on='time_values_nearest', how='left').drop_duplicates()
        # # Define loss function for each data point (MSE for the moment)
        # def get_loss(row):
        #     return (row['value_real'] - row['value_target']) ** 2
        # # Aggregate errors
        # limits['loss'] = limits.apply(get_loss, 1)
        # loss_value = np.mean(limits['loss'].tolist())
        # return loss_value
        df_actual_path = df_actual_path.rename(columns={'target_values_actual_path': 'actual_values'})
        df_constrained = df_constrained.rename(columns={'target_values_constrained_path': 'target_values'})
        df_constrained = df_constrained[df_constrained['time_values'] <= df_actual_path['time_values'].max()]
        xs = df_actual_path['time_values'].tolist()
        ys = df_actual_path['actual_values'].tolist()
        # logger.debug('Calculations 2') 
        def get_prev_and_next_times(row):
            t_constrain = row[0]
            # logger.debug(t_constrain)
            index_time = min(enumerate(xs), key=lambda x: abs(x[1]-t_constrain))[0]
            prev_time_index = index_time - 1 if index_time - 1 >= 0 else 0
            next_time_index = index_time + 1 if index_time + 1 < len(xs) else len(xs)-1
            prev_value = ys[prev_time_index]
            next_value = ys[next_time_index]
            prev_time = xs[prev_time_index]
            next_time = xs[next_time_index]
            new_row = [prev_time, next_time, prev_value, next_value]
            # logger.debug(new_row)
            return pd.Series(new_row)
        # Apply function
        df_constrained[['prev_time', 'next_time', 'prev_value', 'next_value']] = df_constrained[['time_values']].apply(get_prev_and_next_times, 1)
        def make_linear_regression(row):
            return row['prev_value'] + (row['time_values'] - row['prev_time']) * (row['next_value'] - row['prev_value']) / (row['next_time'] - row['prev_time'])
        df_constrained['value_regression'] = df_constrained.apply(make_linear_regression, 1)
        df_constrained['loss'] = (df_constrained['target_values'] - df_constrained['value_regression'])**2
        loss_value = df_constrained['loss'].mean()
        # Retval.
        return loss_value

    # Weighting objective function definition
    def weighting_objective_function_and_path_loss(val):

        # Fetch path from file
        df_actual = pd.read_csv(results_dirname, index_col=False)[['time', target_var_name]]
        df_actual_path = pd.DataFrame(columns=['time_values', 'target_values_actual_path'])
        df_actual_path['time_values'] = df_actual['time'].tolist()
        df_actual_path['target_values_actual_path'] = df_actual[target_var_name].tolist()

        loss_path_trajectory = loss_function_path_trajectory(df_constrained_path.copy(), df_actual_path)

        # TODO: allow alpha < 0.01 en OpenModelica
        # alpha_value = 0.00001
        # alpha_value = 0.0

        if max_or_min == "min":
            # logger.debug(alpha_value * val + (1 - alpha_value) * loss_path_trajectory)
            return alpha_value * val + (1 - alpha_value) * loss_path_trajectory
        else:
            # logger.debug(alpha_value * val - (1 - alpha_value) * loss_path_trajectory)
            return alpha_value * val - (1 - alpha_value) * loss_path_trajectory

    # Objective function definition
    def objectiveFunction(params_vals):

        # logger.debug('objective Function params')
        # logger.debug(params_vals)

        # Organize param vals
        params_vals_dict = {p_name: p_val for p_name, p_val in zip(parameters_to_perturb, params_vals)}

        # Run a quick simulation
        var_val = compiled_model.quickSimulate(target_var_name, params_vals_dict)

        # Apply weighting using 1. path loss and 2. value of objective variable returned by simulations
        objective_result = weighting_objective_function_and_path_loss(var_val)

        # Assign a sign depending if maximizing or minimizing
        if max_or_min == "max":
            return -objective_result
        elif max_or_min == "min":
            return objective_result
        else:
            raise Exception('Error')

    # Return objective function
    return objectiveFunction


# Auxs
def createObjectiveFunctionForModel(compiled_model, param_names, target_var_name, max_or_min):
    # We initialize a function with "dynamic hardcoded variables". It will have this variables fixed with the value
    # from execution context of the function that defined it

    def objectiveFunction(params_vals):

        # logger.debug('Run objective function')

        # Organize param vals
        params_vals_dict = {p_name: p_val for p_name, p_val in zip(param_names, params_vals)}

        # Run a quick simulation
        var_val = compiled_model.quickSimulate(target_var_name, params_vals_dict)

        # Log simu result
        # x_str = ", ".join([str(x) for x in params_vals])
        # logging_str = "\n   x: {1}\n   f(x) = {0}".format(var_val, x_str)
        # logger.info(logging_str)

        # Assign a sign depending if maximizing or minimizing
        obj_func_val = None
        if max_or_min == "max":
            obj_func_val = -var_val
        elif max_or_min == "min":
            obj_func_val = var_val
        else:
            raise Exception('Error')
        return obj_func_val

    # Return objective function
    return objectiveFunction
