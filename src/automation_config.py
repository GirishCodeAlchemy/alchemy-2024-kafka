import json

import yaml


class AutomationConfig:
    def __init__(self, filename):
        self.filename = filename
        self.data = self.read_yaml_file()

    def read_yaml_file(self):
        try:
            with open(self.filename, 'r') as f:
                yaml_obj = yaml.safe_load(f)
            json_data = json.dumps(yaml_obj, indent=2)
            return json_data
        except yaml.YAMLError as err:
            print(f"Error Parsing YAML data: {err}")
            return None

    def execute_component(self):
        component = self.data.get("Component")

        if component == "connect":
            self.execute_connect_automation()
        elif component == "topic":
            self.execute_topic_automation()
        else:
            print("Component not supported")

    def execute_connect_automation(self):
        print("Executing Connector automation script")
        # Add your Connect Automation logic here

    def execute_topic_automation(self):
        print("Executing Topic automation script")
        # Add your Connect Automation logic here


def main(filename):
    config = AutomationConfig(filename)
    if config.data:
        config.execute_component()
    else:
        print("Failed to read YAML config file.")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print("Please provide the YAML config file name as an argument.")
