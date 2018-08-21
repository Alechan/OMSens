# Std
import os
import xml.etree.ElementTree as ElementTree
import pandas
# Mine
import filesystem.files_aux as files_aux

class CompiledModelicaModel():
    def __init__(self,model_name, binary_file_path):
        # Attrs from args
        self.model_name = model_name
        self.binary_file_path = binary_file_path
        # Other attrs
        xml_file_path = xmlFilePathForModel(self.binary_file_path, self.model_name)
        self.xml_file_path = xml_file_path
        # Read XML from XML file
        xml_tree = ElementTree.parse(self.xml_file_path)
        self.xml_tree = xml_tree

    def setParameterStartValue(self,param_name,param_val):
        # Cast value as string
        param_val_str = str(param_val)
        # Get XML root
        root = self.xml_tree.getroot()
        # Find element with vars and parameters
        modelvars_element = [e for e in root.getchildren() if e.tag == "ModelVariables"][0]
        # Find parameter
        param_element = [x for x in modelvars_element.getchildren()
                         if x.tag == "ScalarVariable" and
                         x.attrib["name"] == param_name][0]
        # Get value element for param
        param_value_element = param_element.getchildren()[0]
        # Change value
        param_value_element.attrib["start"] = param_val_str
        # Write XML to disk
        self.xml_tree.write(self.xml_file_path)

    def simulate(self, dest_csv_path):
        # Get folder for binary
        binary_folder_path = os.path.dirname(self.binary_file_path)
        # Define command to be called
        binary_args = "-r={0}".format(dest_csv_path)
        cmd = "{0} {1}".format(self.binary_file_path, binary_args)
        # Execute binary with args
        output = files_aux.callCMDStringInPath(cmd, binary_folder_path)
        # Define run log file path
        simu_folder_path = os.path.dirname(dest_csv_path)
        csv_name = os.path.basename(dest_csv_path)
        simu_log_name = "run_{0}.txt".format(csv_name)
        simu_log_path = os.path.join(simu_folder_path, simu_log_name)
        # Write log to disk
        output_decoded = output.decode("UTF-8")
        files_aux.writeStrToFile(output_decoded, simu_log_path)
        return output_decoded

    def simulateAndReadResults(self, dest_csv_path):
        self.simulate(dest_csv_path)
        df_simu = pandas.read_csv(dest_csv_path)
        return df_simu

# Auxs
def xmlFilePathForModel(binary_file_path, model_name):
    binary_folder_path = os.path.dirname(binary_file_path)
    xml_file_name = "{0}_init.xml".format(model_name)
    xml_file_path = os.path.join(binary_folder_path, xml_file_name)
    return xml_file_path
