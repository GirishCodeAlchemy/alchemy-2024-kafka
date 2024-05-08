#!/usr/bin/python3

import json
import sys
from subprocess import PIPE, Popen

import requests

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
        self.cacert = "cacerts.pem"
        self.key = "ca.key"
        self.cer = "ca.cer"

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
        if self.env == "stage":
            server = "stage-kafka-connect"

        url = f"https://{server}:8083"
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
        try:
            # Send the HTTP request with authentication and headers
            response = requests.request(method, url, headers=headers,
                auth=self.auth, data=json.dumps(data) if data else None,
                verify=self.cacert, cert=(self.cer,self.key))
            response.raise_for_status()  # Raise an exception for non-2xx status codes
            print(json.dumps(response.json(), indent=4))

        except requests.exceptions.RequestException as e:
            print(f"Error making request to Kafka connector: {e}")
            sys.exit(1)

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
            self.request_kafka(method, f"{self.url}/connectors")

        elif command == "get connector":
            # Ensure a connector name is provided as the second argument
            if len(self.argv) < 2:
                print("Please provide a connector name for the get operation")
                return
            connector = self.argv[1]
            print(f"\nGet the connector config: {connector} for {self.env}\n")
            self.request_kafka(method, f"{self.url}/connectors/{connector}/config")

        elif command == "get connector status":
            if len(self.argv) < 2:
                print("Please provide a connector name for the get status operation")
                return
            connector = self.argv[1]
            print(f"\nGet the connector status: {connector} for {self.env}\n")
            self.request_kafka(method, f"{self.url}/connectors/{connector}/status")

        elif command == "create connector":
            # Ensure a connector configuration file is provided as the second argument
            if len(self.argv) < 2:
                print("Please provide a connector configuration file for the create operation")
                return
            data_file = self.argv[1]
            # Read data from the connector configuration file (implementation not shown)
            with open(data_file, "r") as f:
                data = json.load(f)
            print(f"\nCreated the connector in {self.env}\n")
            self.request_kafka("POST", f"{self.url}/connectors", data=data)

        elif command == "update connector":
            # Ensure a connector configuration file is provided as the second argument
            if len(self.argv) < 3:
                print("Please provide a connector configuration file for the Update operation")
                return
            connector = self.argv[1]
            data_file = self.argv[2]
            # Read data from the connector configuration file (implementation not shown)
            with open(data_file, "r") as f:
                data = json.load(f)
            print(f"\nUpdating the connector in {self.env}\n")
            self.request_kafka("PUT", f"{self.url}/connectors/{connector}/config", data=data)

        elif command == "delete connector":
            if len(self.argv) < 2:
                print("Please provide a connector name for the delete operation")
                return
            connector = self.argv[1]
            print(f"\Delete the connector: {connector} for {self.env}\n")
            self.request_kafka("DELETE", f"{self.url}/connectors/{connector}")

        elif command == "restart connector":
            if len(self.argv) < 2:
                print("Please provide a connector name for the restart operation")
                return
            connector = self.argv[1]
            print(f"\Restart the connector: {connector} for {self.env}\n")
            self.request_kafka(method, f"{self.url}/connectors/{connector}/restart")

        elif command == "pause connector":
            if len(self.argv) < 2:
                print("Please provide a connector name for the pause operation")
                return
            connector = self.argv[1]
            print(f"\Pause the connector: {connector} for {self.env}\n")
            self.request_kafka(method, f"{self.url}/connectors/{connector}/pause")

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
    print("\tstatus <connector_name>                      - Gets the status of connectors")
    print("\tcreate <connector_json>                      - Creates a connector using a configuration json")
    print("\tupdate <connector_name> <connector_json>     - Updates the configuration of a connector")
    print("\tdelete <connector_name>                      - Deletes a specific connector")
    print("\trestart <connector_name>                     - Restarts a specific connector")
    print("\tpause <connector_name>                       - Pauses a specific connector\n")
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
