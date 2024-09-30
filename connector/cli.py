#!/Users/girish/Desktop/workspace/py310/bin/python
import argparse
import json
import os
import sys
from subprocess import PIPE, Popen

import requests
from dotenv import load_dotenv

load_dotenv()


def load_config():
    """
    Load the Kafka environment config from the JSON file

    Returns:
        dict: Kafka configuration (env, user, password, cert paths, server, port)
    """
    try:
        if os.path.exists(KafkaConnectorManager.CONFIG_FILE):
            with open(KafkaConnectorManager.CONFIG_FILE, "r") as config_file:
                return json.load(config_file)
    except Exception as e:
        print(f"Error loading config: {e}")

    return {"current_context": None, "environments": {}}

class KafkaConnectorManager:
    CONFIG_DIR = os.path.expanduser("~/.connector_cli")
    CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

    def __init__(self, env, args):
        """
        Class constructor

        Args:
            env (str): The Kafka environment (e.g., dev, prod)
            args (Namespace): Parsed arguments from argparse
        """
        self.env = env
        self.args = args

        # Load saved configuration
        self.config = load_config()
        self.active_env = self.get_active_env()


    def get_active_env(self):
        env_name = self.config.get('current_context')
        if env_name:
            return self.config['environments'][env_name]
        else:
            print("No active environment found. Set an environment first.")
            return None

    @staticmethod
    def ensure_config_dir():
        """
        Ensure the configuration directory exists
        """
        if not os.path.exists(KafkaConnectorManager.CONFIG_DIR):
            os.makedirs(KafkaConnectorManager.CONFIG_DIR)

    def save_config(self):
        """
        Save the Kafka environment config to a JSON file

        Args:
            env (str): Kafka environment (e.g., dev, stage)
            user (str): Kafka user
            password (str): Kafka password
            cacert (str): Path to the CA certificate
            key (str): Path to the key file
            cer (str): Path to the certificate file
            server (str): Kafka server host URL
            port (int): Kafka server port
        """
        KafkaConnectorManager.ensure_config_dir()

        with open(KafkaConnectorManager.CONFIG_FILE, "w") as config_file:
            json.dump(self.config, config_file, indent=4)

    def set_env(self, args):
        # Save environment details
        env_name = args.env
        self.config['environments'][env_name] = {
            "user": args.user,
            "password": args.password,
            "cacert": args.cacert,
            "key": args.key,
            "cer": args.cer,
            "server": args.server,
            "port": args.port,
        }
        # Set it as the current context
        self.config['current_context'] = env_name
        self.save_config()
        print(f"Environment '{env_name}' is set and activated.")

    # @staticmethod


    def use_env(self, env_name):
        # Switch active environment context
        if env_name in self.config['environments']:
            self.config['current_context'] = env_name
            self.save_config()
            print(f"Switched to environment: {env_name}")
        else:
            print(f"Environment '{env_name}' not found. Use 'set-env' to add it.")

    def get_current_env(self):
        # Display current environment details
        env_name = self.config.get('current_context')
        if not env_name:
            print("No active environment. Set an environment using 'set-env'.")
            return
        env_details = self.config['environments'][env_name]
        print(f"Current Environment: {env_name}")
        for key, value in env_details.items():
            print(f"{key}: {value}")

    def list_envs(self):
        # List all environments
        if not self.config['environments']:
            print("No environments configured.")
        else:
            print("Available Environments:")
            for env_name in self.config['environments']:
                current_marker = " (current)" if env_name == self.config['current_context'] else ""
                print(f"- {env_name}{current_marker}")

    def fetch_url(self):
        """
        Fetches the URL for Kafka connectors based on the environment

        Returns:
            str: The URL for Kafka connectors
        """
        print(self.active_env)
        protocol = "https" if {self.active_env.get('cacert')} else "http"
        return f"{protocol}://{self.active_env['server']}:{self.active_env['port']}"

    def get_password(self):
        """
        Placeholder function for potentially retrieving password securely
        """
        return ""

    def request_kafka(self, method, endpoint, data=None):
        """
        Sends a request to the Kafka connector API

        Args:
            method (str): The HTTP method for the request (e.g., GET, POST)
            endpoint (str): The API endpoint for Kafka connectors
            data (dict, optional): Data to send in the request body (default: None)

        Returns:
            requests.Response: The response object from the HTTP request
        """
        if not self.active_env:
            print("No active environment to execute commands.")
            return
        url = f"{self.fetch_url()}{endpoint}"
        headers = {
            "Content-Type": "application/json",
        }
        response = None
        try:
            auth = requests.auth.HTTPBasicAuth(self.active_env.get('user'), self.active_env.get('password'))

            if self.active_env.get('cacert'):
                # Combine username and password for authentication
                response = requests.request(
                    method,
                    url,
                    headers=headers,
                    auth=auth,
                    data=json.dumps(data) if data else None,
                    verify=self.active_env.get('cacert'),
                    cert=(self.active_env.get('cer'), self.active_env.get('key')),
                )
            else:
                response = requests.request(
                    method, url, headers=headers, auth=auth, data=json.dumps(data) if data else None
                )

            response.raise_for_status()
            return response

        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
        return response

    def handle_command(self):
        """
        Executes a command to manage Kafka connectors
        """
        command = self.args.command
        method = "GET"

        if command == "list":
            print(f"\nList the connectors for {self.env}\n")
            response = self.request_kafka(method, "/connectors")
            if not response:
                return
            connectors = response.json()
            for each_connector in connectors:
                print(each_connector)

        elif command == "get":
            if not self.args.connector:
                print("Please provide a connector name for the get operation")
                return
            connector = self.args.connector
            print(f"\nGet the connector config: {connector} for {self.env}\n")
            self.request_kafka(method, f"/connectors/{connector}/config")

        elif command == "status":
            connectors = [self.args.connector] if self.args.connector else self.request_kafka(method, "/connectors").json()
            print(f"\nGet the connector status for {self.env}\n")
            for connector in connectors:
                response = self.request_kafka(method, f"/connectors/{connector}/status")
                status = response.json().get("connector", {}).get("state", "")
                print(f"{connector}: {status}")

        elif command == "create":
            if not self.args.config:
                print("Please provide a connector configuration file for the create operation")
                return
            with open(self.args.config) as config_file:
                data = json.load(config_file)
            print(f"\nCreating the connector in {self.env}\n")
            self.request_kafka("POST", "/connectors", data=data)

        elif command == "update":
            if not self.args.connector or not self.args.config:
                print("Please provide a connector name and configuration file for the update operation")
                return
            with open(self.args.config) as config_file:
                data = json.load(config_file)
            print(f"\nUpdating the connector in {self.env}\n")
            self.request_kafka("PUT", f"/connectors/{self.args.connector}/config", data=data)

        elif command == "delete":
            if not self.args.connector:
                print("Please provide a connector name for the delete operation")
                return
            connector = self.args.connector
            print(f"\nDeleting the connector: {connector} for {self.env}\n")
            self.request_kafka("DELETE", f"/connectors/{connector}")

        elif command == "restart":
            connectors = [self.args.connector] if self.args.connector else self.request_kafka(method, "/connectors").json()
            for connector in connectors:
                print(f"\nRestarting connector: {connector}\n")
                self.request_kafka("POST", f"/connectors/{connector}/restart")

        elif command == "pause":
            connectors = [self.args.connector] if self.args.connector else self.request_kafka(method, "/connectors").json()
            for connector in connectors:
                print(f"\nPausing connector: {connector}\n")
                self.request_kafka("PUT", f"/connectors/{connector}/pause")

        elif command == "resume":
            connectors = [self.args.connector] if self.args.connector else self.request_kafka(method, "/connectors").json()
            for connector in connectors:
                print(f"\nResuming connector: {connector}\n")
                self.request_kafka("PUT", f"/connectors/{connector}/resume")

        elif command == "set-env":
            self.set_env(self.args)
            # KafkaConnectorManager.save_config(
            #     self.args.env, self.args.user, self.args.password, self.args.cacert, self.args.key, self.args.cer,
            #     self.args.server, self.args.port
            # )
            print(f"Environment set to: {self.args.env}")

        # elif command == "get-env":
        #     config = KafkaConnectorManager.load_config()
        #     print(f"Current environment: {config.get('env')}")
        #     print(f"User: {config.get('user')}")
        #     print(f"Server: {config.get('server')}")
        #     print(f"Port: {config.get('port')}")
        #     print(f"CA Cert: {config.get('cacert')}")
        #     print(f"Key: {config.get('key')}")
        #     print(f"Cert: {config.get('cer')}")
        elif command == "use-env":
            self.use_env(self.args.env)
        elif command == "get-env":
            self.get_current_env()
        elif command == "list-env":
            self.list_envs()
        else:
            print(f"Unknown command: {command}")


def main():
    """
    Main function - starting point of the script

    Parses command-line arguments and creates a KafkaConnectorManager object.
    """
    parser = argparse.ArgumentParser(description="Kafka Connect Management CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Connector commands
    subparsers.add_parser("list", help="List all connectors")
    parser_get = subparsers.add_parser("get", help="Get a connector config")
    parser_get.add_argument("connector", help="Connector name")
    parser_status = subparsers.add_parser("status", help="Get connector status")
    parser_status.add_argument("connector", help="Connector name", nargs="?")
    parser_create = subparsers.add_parser("create", help="Create a connector")
    parser_create.add_argument("config", help="Connector config JSON file")
    parser_update = subparsers.add_parser("update", help="Update a connector")
    parser_update.add_argument("connector", help="Connector name")
    parser_update.add_argument("config", help="Connector config JSON file")
    parser_delete = subparsers.add_parser("delete", help="Delete a connector")
    parser_delete.add_argument("connector", help="Connector name")
    parser_restart = subparsers.add_parser("restart", help="Restart a connector")
    parser_restart.add_argument("connector", help="Connector name", nargs="?")
    parser_pause = subparsers.add_parser("pause", help="Pause a connector")
    parser_pause.add_argument("connector", help="Connector name", nargs="?")
    parser_resume = subparsers.add_parser("resume", help="Resume a connector")
    parser_resume.add_argument("connector", help="Connector name", nargs="?")

    # Environment commands
    parser_set_env = subparsers.add_parser("set-env", help="Set environment")
    parser_set_env.add_argument("env", help="Environment (dev, stage, prod)")
    parser_set_env.add_argument("--user", help="Kafka user")
    parser_set_env.add_argument("--password", help="Kafka password")
    parser_set_env.add_argument("--cacert", help="CA certificate file")
    parser_set_env.add_argument("--key", help="Key file")
    parser_set_env.add_argument("--cer", help="Certificate file")
    parser_set_env.add_argument("--server", help="Kafka server host URL", default="localhost")
    parser_set_env.add_argument("--port", help="Kafka server port", type=int, default=8083)

    # Use environment command (switch context)
    parser_use_env = subparsers.add_parser("use-env", help="Switch to a specific environment")
    parser_use_env.add_argument("env", help="Environment name to switch to")

    # Get current environment command
    subparsers.add_parser("get-env", help="Get current environment details")

    # List all environments command
    subparsers.add_parser("list-env", help="List all configured environments")

    # Load environment from config if not provided
    args = parser.parse_args()
    env = args.env if hasattr(args, "env") else load_config().get("current_context")

    if not env:
        print("Please set the environment using the 'set-env' command.")
        sys.exit(1)

    # Create KafkaConnectorManager instance and handle the command
    manager = KafkaConnectorManager(env, args)
    manager.handle_command()


if __name__ == "__main__":
    main()
