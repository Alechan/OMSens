# Std
import os
import xml.etree.ElementTree as ElementTree
import pandas
import copy

# Mine
import filesystem.files_aux as files_aux
import running.simulation_run_info as simu_run_info

class CompiledModelicaModel():
    def __init__(self,model_name, binary_file_path):
        # Attrs from args
        self.model_name = model_name
        self.binary_file_path = binary_file_path
        xml_file_path = xmlFilePathForModel(self.binary_file_path, self.model_name)
        self.xml_file_path = xml_file_path
        # Read XML from XML file
        xml_tree = ElementTree.parse(self.xml_file_path)
        self.xml_tree = xml_tree
        # Save a copy of the xml with the original values
        self.default_xml_tree = copy.deepcopy(xml_tree)

    # Getters
    def parameterValue(self,param_name):
        # Get XML element for param and its value from the (changed) XML
        xml_tree = self.xml_tree
        param_val_casted = parameterValueInModelicaXML(param_name, xml_tree)
        return param_val_casted

    def defaultParameterValue(self,param_name):
        # Get XML element for param and its value from the original XML
        xml_tree = self.default_xml_tree
        param_val_casted = parameterValueInModelicaXML(param_name, xml_tree)
        return param_val_casted

    # Setters
    def setParameterStartValue(self,param_name,param_val):
        # Cast value as string
        param_val_str = str(param_val)
        # Get XML element for param and its value
        param_value_element = valueElementForParamAndXMLTree(param_name, self.xml_tree)
        # Change value
        param_value_element.attrib["start"] = param_val_str
        # Write XML to disk
        self.xml_tree.write(self.xml_file_path)

    # Other
    def simulate(self, dest_csv_path, flags=""):
        # Get folder for binary
        binary_folder_path = os.path.dirname(self.binary_file_path)
        # Define command to be called
        binary_args = "-r={0}".format(dest_csv_path)
        cmd = "{0} {1} {2}".format(self.binary_file_path, binary_args, flags)
        # Execute binary with args
        output = files_aux.callCMDStringInPath(cmd, binary_folder_path)
        # Parse log
        output_decoded = output.decode("UTF-8")
        # Create simulation results instance
        simu_results = simu_run_info.SimulationResults(dest_csv_path, self.model_name, self.binary_file_path,
                                                       output_decoded)
        return simu_results

    def quickSimulate(self,var_name):
        # Get folder for binary
        binary_folder_path = os.path.dirname(self.binary_file_path)
        # Define command to be called
        binary_args = "-output {0}".format(var_name)
        flags = "-lv=-LOG_SUCCESS"
        cmd = "{0} {1} {2}".format(self.binary_file_path, binary_args, flags)
        # Execute binary with args
        output = files_aux.callCMDStringInPath(cmd, binary_folder_path)
        # Decode stdout
        output_decoded = output.decode("UTF-8")
        # Parse output to get results
        var_output_str = output_decoded.split(",")[1]
        var_val_str = var_output_str.split("=")[1]
        var_val = float(var_val_str)
        return var_val

    def restoreAllParametersToDefaultValues(self):
        # Set the default xml tree as the model xml tree
        self.xml_tree = self.default_xml_tree
        # Save a copy of the xml with the original values so we can change the xml tree freely again
        self.default_xml_tree = copy.deepcopy(self.xml_tree)


# Auxs
def xmlFilePathForModel(binary_file_path, model_name):
    binary_folder_path = os.path.dirname(binary_file_path)
    xml_file_name = "{0}_init.xml".format(model_name)
    xml_file_path = os.path.join(binary_folder_path, xml_file_name)
    return xml_file_path


def valueElementForParamAndXMLTree(param_name, xml_tree):
    # Get XML root
    root = xml_tree.getroot()
    # Find element with vars and parameters
    modelvars_element = [e for e in root.getchildren() if e.tag == "ModelVariables"][0]
    # Find parameter
    param_element = [x for x in modelvars_element.getchildren()
                     if x.tag == "ScalarVariable" and
                     x.attrib["name"] == param_name][0]
    # Get value element for param
    param_value_element = param_element.getchildren()[0]
    return param_value_element


def parameterValueInModelicaXML(param_name, xml_tree):
    param_value_element = valueElementForParamAndXMLTree(param_name, xml_tree)
    # Get val from element
    param_val = param_value_element.attrib["start"]
    # Cast it to its type
    param_val_casted = castModelicaValue(param_val, param_value_element)
    return param_val_casted


def castModelicaValue(param_val, param_value_element):
    modelica_type = param_value_element.tag
    if modelica_type == "Real":
        param_val_casted = float(param_val)
    else:
        error_msg = "The script has not been yet adapted to cast Modelica types of {0}".format(modelica_type)
        raise Exception(error_msg)
    return param_val_casted
