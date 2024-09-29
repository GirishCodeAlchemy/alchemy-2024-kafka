#!/Users/girish/Desktop/workspace/py310/bin/python
import argparse
import json
import os
import sys
from subprocess import PIPE, Popen

import requests
from dotenv import load_dotenv

load_dotenv()

CONFIG_PATH = os.path.expanduser("~/.kafkactl/config.json")

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=4)

def set_config(env, server_url):
    config = load_config()
    config[env] = {"url": server_url}
    save_config(config)
    print(f"Config for '{env}' set successfully.")

def get_config(env):
    config = load_config()
    if env in config:
        print(f"Config for '{env}': {config[env]}")
    else:
        print(f"No config found for '{env}'.")

class KafkaConnectorManager:
    def __init__(self, env, argv):
        self.env = env
        self.argv = argv
        config = load_config()
        if env in config:
            self.url = config[env]["url"]
        else:
            print(f"No config found for environment '{env}'")
            sys.exit(1)

        self.user = "connect"
        self.password = self.get_password()
        self.cacert = os.getenv("CACERT")
        self.key = os.getenv("CA_KEY")
        self.cer = os.getenv("CA_CER")
        self.auth = requests.auth.HTTPBasicAuth(self.user, self.password)

    def get_password(self):
        return ""

    def request_kafka(self, method, url, data=None):
        headers = {
            "Content-Type": "application/json",
        }
        response = None
        try:
            if self.cacert:
                response = requests.request(method, url, headers=headers,
                                            auth=self.auth, data=data if data else None,
                                            verify=self.cacert, cert=(self.cer, self.key))
            else:
                response = requests.request(method, url, headers=headers,
                                            auth=self.auth, data=data if data else None)

            response.raise_for_status()
        except requests.exceptions.RequestException:
            print(f"Error: {response.json().get('message')}")
        return response

    def handle_command(self):
        COMMANDS = {
            "list": "list connectors",
            "get": "get connector",
            "status": "get connector status",
            "create": "create connector",
            "update": "update connector",
            "delete": "delete connector",
            "restart": "restart connector",
            "pause": "pause connector",
            "resume": "resume connector"
        }

        command = self.argv[0]
        if command not in COMMANDS:
            print(f"Command '{command}' is not supported")
            return

        if command == "list":
            response = self.request_kafka("GET", f"{self.url}/connectors")
            print(f"List of connectors for {self.env}:\n")
            for connector in response.json():
                print(connector)

        # Add more command handling logic similar to the original script

def main():
    parser = argparse.ArgumentParser(description="Kafka Connector Management CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Subparser for setting config
    set_parser = subparsers.add_parser("set-config", help="Set config for a Kafka environment")
    set_parser.add_argument("env", help="Environment name (e.g., dev, prod)")
    set_parser.add_argument("server_url", help="Kafka server URL")

    # Subparser for getting config
    get_parser = subparsers.add_parser("get-config", help="Get config for a Kafka environment")
    get_parser.add_argument("env", help="Environment name (e.g., dev, prod)")

    # Subparser for Kafka connector management commands
    manage_parser = subparsers.add_parser("manage", help="Manage Kafka connectors")
    manage_parser.add_argument("env", help="Environment name (e.g., dev, prod)")
    manage_parser.add_argument("command", help="Command for managing connectors (list, get, status, create, etc.)")
    manage_parser.add_argument("args", nargs=argparse.REMAINDER, help="Additional arguments for the command")

    args = parser.parse_args()

    if args.command == "set-config":
        set_config(args.env, args.server_url)
    elif args.command == "get-config":
        get_config(args.env)
    elif args.command == "manage":
        manager = KafkaConnectorManager(args.env, args.args)
        manager.handle_command()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
