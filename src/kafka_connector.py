#!/Users/girish/Desktop/workspace/py310/bin/python
import json
import os
import sys
from subprocess import PIPE, Popen

import requests
from dotenv import load_dotenv

load_dotenv()
# sys.path.append("/opt/confluent/scripts")

# from utils import get_server_details

class KafkaConnectorManager:
    def __init__(self, env, argv):
        """
        Class constructor

        Args:
            env (str): The Kafka environment (e.g., dev, prod)
            argv (list): The command-line arguments passed to the script
        """
        self.env = env
        self.user = "connect"
        self.password = self.get_password()
        self.cacert = os.getenv("CACERT")
        self.key = os.getenv("CA_KEY")
        self.cer = os.getenv("CA_CER")

        # Combine username and password for authentication
        self.auth = requests.auth.HTTPBasicAuth(self.user, self.password)

        # Call function to fetch the URL based on environment (implementation assumed in fetch_url)
        self.url = self.fetch_url()

        self.argv = argv

    def fetch_url(self):
        """
        Fetches the URL for Kafka connectors based on the environment

        Returns:
            str: The URL for Kafka connectors
        """
        server = "localhost"
        url = ""
        if self.env == "stage":
            server = "stage-kafka-connect"

        if self.cacert:
            url = f"https://{server}:8083"
        else:
            url = f"http://{server}:8083"
        return url

    def get_password(self):
        """
        Placeholder function for potentially retrieving password securely

        This function is not currently used in the script but might have been intended for an alternative password retrieval method.
        """
        # self.password = Popen(['ssh -o StrictHostKeyChecking=no  localhost "/home/confluent/password.sh ' + self.user + '"'], shell=True, stdout=PIPE).communicate()[0].decode("utf -8").strip("\n")
        self.password = ""

    def request_kafka(self, method, url, data=None):
        """
        Sends a request to the Kafka connector API

        This function likely sends an HTTP request (GET, POST, etc.) to the specified URL for managing Kafka connectors.

        Args:
            method (str): The HTTP method for the request (e.g., GET, POST)
            url (str): The URL for the Kafka connector API endpoint
            data (dict, optional): Data to send in the request body (default: None)

        Returns:
            requests.Response: The response object from the HTTP request
        """

        headers = {
            "Content-Type": "application/json",
        }
        response = None
        try:

            if self.cacert:
                # Send the HTTPS request with authentication and headers
                response = requests.request(method, url, headers=headers,
                    auth=self.auth, data=data if data else None,
                    verify=self.cacert, cert=(self.cer,self.key))

            else:
                response = requests.request(method, url, headers=headers,
                    auth=self.auth, data=data if data else None)

            response.raise_for_status()  # Raise an exception for non-2xx status codes
            # if method != "DELETE":
            #     print(json.dumps(response.json(), indent=4))
            # else:
            #     print(f"Deleted: {response.status_code}")

        except requests.exceptions.RequestException:
            print(f"Error: {response.json().get('message')}")
        return response

    def handle_command(self):
        """
        Executes a command to manage Kafka connectors

        This function likely parses the command-line arguments to determine the desired action (list, get, status, create, update, delete, restart, pause)
        and performs the corresponding operations on Kafka connectors using the `request_kafka` function.

        Returns:
            None
        """

        # Expected commands (modify as needed)
        COMMANDS = {
            "list": "list connectors",
            "get": "get connector",
            "status": "get connector status",
            "create": "create connector",
            "update": "update connector",
            "delete": "delete connector",
            "restart": "restart connector",
            "pause": "pause connector",
            "resume": "resume connector",
            "list-secret": "list secrets",
            "find-secret": "find secrets",
            "set-secret": "set secrets",
            "delete-secret": "delete secrets"
        }

        # Check if a valid command is provided as the first argument
        if self.argv[0] not in COMMANDS:
            print(f"\n command: {self.argv[0]} is not supported\n")
            return

        command = COMMANDS[self.argv[0]]
        method = "GET"
        # Handle different commands based on a dictionary lookup
        if command == "list connectors":
            print(f"\nList the connectors for {self.env}\n")
            response = self.request_kafka(method, f"{self.url}/connectors")
            print("{:<50} ".format("Connector Name"))
            print("{:<50} ".format("-"*50))
            for each_connector in response.json():
                print("{:<50} ".format(each_connector))

        elif command == "get connector":
            # Ensure a connector name is provided as the second argument
            if len(self.argv) < 2:
                print("Please provide a connector name for the get operation")
                return
            connector = self.argv[1]
            print(f"\nGet the connector config: {connector} for {self.env}\n")
            self.request_kafka(method, f"{self.url}/connectors/{connector}/config")

        elif command == "get connector status":
            if len(self.argv)==1:
                connectors = self.request_kafka(method, f"{self.url}/connectors")
                connectors = [connector for connector in connectors.json()]
            else:
                connectors = [self.argv[1]]
            print(f"\nGet the connector status for {self.env}\n")
            print("{:<50} {:<20}".format("Connector Name", "Status"))
            print("{:<50} {:<20}".format("-"*40, "-"*20))
            for connector in connectors:
                response = self.request_kafka(method, f"{self.url}/connectors/{connector}/status")
                status = response.json().get("connector", {}).get("state", "")
                print("{:<50} {:<20}".format(connector, status))
            print("-"*80)

        elif command == "create connector":
            # Ensure a connector configuration file is provided as the second argument
            if len(self.argv) < 2:
                print("Please provide a connector configuration file for the create operation")
                return
            data = self.argv[1]
            print(f"\nCreated the connector in {self.env}\n")
            self.request_kafka("POST", f"{self.url}/connectors", data=data)

        elif command == "update connector":
            # Ensure a connector configuration file is provided as the second argument
            if len(self.argv) < 3:
                print("Please provide a connector configuration file for the Update operation")
                return
            connector = self.argv[1]
            data = self.argv[2]
            print(f"\nUpdating the connector in {self.env}\n")
            self.request_kafka("PUT", f"{self.url}/connectors/{connector}/config", data=data)

        elif command == "delete connector":
            if len(self.argv) < 2:
                print("Please provide a connector name for the delete operation")
                return
            connector = self.argv[1]
            print(f"\nDelete the connector: {connector} for {self.env}\n")
            self.request_kafka("DELETE", f"{self.url}/connectors/{connector}")

        elif command == "restart connector":
            if len(self.argv)==1:
                connectors = self.request_kafka(method, f"{self.url}/connectors")
                connectors = [connector for connector in connectors.json()]
            else:
                connectors = [self.argv[1]]
            print(f"\nRestart the connector for {self.env}\n")
            print("{:<50} {:<30} {:<20}".format("Connector Name", "Current State", "Status"))
            print("{:<50} {:<30} {:<20}".format("-"*40, "-"*20, "-"*20))
            for connector in connectors:
                response = self.request_kafka(method, f"{self.url}/connectors/{connector}/status")
                status = response.json().get("connector", {}).get("state", "")
                response = self.request_kafka("POST", f"{self.url}/connectors/{connector}/restart")
                print("{:<50} {:<30} {:<20}".format(connector, status, f"Restarted- {response.status_code}"))
            print("-"*80)
        elif command == "pause connector":
            if len(self.argv)==1:
                connectors = self.request_kafka(method, f"{self.url}/connectors")
                connectors = [connector for connector in connectors.json()]
            else:
                connectors = [self.argv[1]]
            print(f"\nPause the connector for {self.env}\n")
            print("{:<50} {:<30} {:<20}".format("Connector Name", "Current State", "Status"))
            print("{:<50} {:<30} {:<20}".format("-"*40, "-"*20, "-"*20))
            for connector in connectors:
                response = self.request_kafka(method, f"{self.url}/connectors/{connector}/status")
                status = response.json().get("connector", {}).get("state", "")
                response = self.request_kafka("PUT", f"{self.url}/connectors/{connector}/pause")
                print("{:<50} {:<30} {:<20}".format(connector, status, f"Paused- {response.status_code}"))
            print("-"*80)
        elif command == "resume connector":
            if len(self.argv)==1:
                connectors = self.request_kafka(method, f"{self.url}/connectors")
                connectors = [connector for connector in connectors.json()]
            else:
                connectors = [self.argv[1]]
            print(f"\Resume the connector for {self.env}\n")
            print("{:<50} {:<30} {:<20}".format("Connector Name", "Current State", "Status"))
            print("{:<50} {:<30} {:<20}".format("-"*40, "-"*20, "-"*20))
            for connector in connectors:
                response = self.request_kafka(method, f"{self.url}/connectors/{connector}/status")
                status = response.json().get("connector", {}).get("state", "")
                response = self.request_kafka("PUT", f"{self.url}/connectors/{connector}/resume")
                print("{:<50} {:<30} {:<20}".format(connector, status, f"Resume- {response.status_code}"))
            print("-"*80)
        elif command == "list secrets":
            print(f"\nFetch all the connector secrets for {self.env}\n")
            self.request_kafka(method, f"{self.url}/secret/paths/")
        elif command == "find secrets":
            connector_secret = self.argv[1]
            print(f"\nFetch the connector secrets for {self.env}\n")
            self.request_kafka(method, f"{self.url}/secret/paths/{connector_secret}/keys/")

        elif command == "set secrets":
            if len(self.argv) < 2:
                print("Please provide a connector name for the set secret operation")
                return
            connector = self.argv[1]
            secret = json.dumps({"secret": self.argv[2]})
            print(f"\nSet the secret for connector: {connector} in {self.env}\n")
            try:
                self.request_kafka("POST", f"{self.url}/secret/paths/{connector}/keys/auth/version", data=secret)
            except Exception as e:
                print(f"Failed to Create the connector secret {connector}, Error: {e}")

        elif command == "delete secrets":
            connector_secret = self.argv[1]
            print(f"\nDelete the connector secrets for {self.env}\n")
            try:
                self.request_kafka("DELETE", f"{self.url}/secret/paths/{connector_secret}")
                print(f"Successfully deleted the connector secret {connector_secret}")
            except Exception as e:
                print(f"Failed to delete the connector secret {connector_secret}, Error: {e}")

        # elif command in ("restart connector", "pause connector"):
        #     # Implement logic for these commands
        #     print(f"Command: {command} is not currently implemented\n")

        else:
            print(f"Unexpected command: {command}\n")


def usage(argv):
    """
    Prints usage information for the script

    This function displays a message explaining how to use the script and the available commands for managing Kafka connectors.
    """
    print("###############################################")
    print("#      Kafka Connector Management Script      #")
    print("###############################################")
    print(f"\nUsage: {argv[0]} <environment> <command> [<connector_name> <connector_config_file>]\n")
    print("<environment> (required): The Kafka environment (e.g., dev, prod)")
    print("<command> (required): The desired action for Kafka connectors:\n")
    print("\n Available commands:")
    print("\tlist                                         - Lists all connectors")
    print("\tget <connector_name>                         - Gets the configuration of a specific connector")
    print("\tstatus                                       - Gets the status of all connectors")
    print("\tstatus <connector_name>                      - Gets the status of connectors")
    print("\tcreate <connector_json>                      - Creates a connector using a configuration json")
    print("\tupdate <connector_name> <connector_json>     - Updates the configuration of a connector")
    print("\tdelete <connector_name>                      - Deletes a specific connector")
    print("\trestart <connector_name>                     - Restarts a specific connector")
    print("\tpause                                        - Pauses all the connectors\n")
    print("\tpause <connector_name>                       - Pauses a specific connector\n")
    print("\tresume                                       - Resumes all the connectors\n")
    print("\tresume <connector_name>                      - Resumes a specific connector\n")
    print("\tget-secret                                   - Get Secrets for the specific environment\n")
    print("\tset-secret <connector_name> <user:pwd>       - Set the secret for a specific connector\n")
    print("\t<connector_name> (optional): The name of the connector (required for get, delete, restart, pause operations)")
    print("\t<connector_json> (optional): connector configuration json (required for create & update operation)")
    print("\n")


def main():
    """
    Main function - starting point of the script

    Parses command-line arguments and creates a KafkaConnectorManager object
    """
    if len(sys.argv) < 3:
        usage(sys.argv)
        sys.exit(1)

    env = sys.argv[1]
    command = sys.argv[2:]

    # Create KafkaConnectorManager object
    manager = KafkaConnectorManager(env, command)

    # Handle commands (implementation assumed in handle_command)
    manager.handle_command()


if __name__ == "__main__":
    main()
