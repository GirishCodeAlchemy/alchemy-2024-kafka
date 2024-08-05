import json
import os
import sys

import requests


class KafkaTopicManager:
    def __init__(self, env):
        """
        Class constructor

        Args:
            env (str): The Kafka environment (e.g., dev, prod)
        """
        self.env = env
        self.user = "admin"
        self.password = "password"  # Update with actual password
        self.url = self.get_url()

    def get_url(self):
        """
        Fetches the URL for Kafka Admin API based on the environment

        Returns:
            str: The URL for Kafka Admin API
        """
        server = "localhost"  # Default server
        if self.env == "stage":
            server = "stage-kafka"  # Update with actual stage server
        return f"http://{server}:8082"

    def create_topic(self, topic_name, partitions=1, replication_factor=1):
        """
        Creates a Kafka topic

        Args:
            topic_name (str): The name of the topic to be created
            partitions (int): The number of partitions for the topic (default: 1)
            replication_factor (int): The replication factor for the topic (default: 1)

        Returns:
            dict: Response JSON
        """
        url = f"{self.url}/topics/{topic_name}"
        headers = {"Content-Type": "application/json"}
        data = {
            "partitions": partitions,
            "replicationFactor": replication_factor
        }
        response = requests.post(url, headers=headers, auth=(self.user, self.password), json=data)
        return response.json()

    def delete_topic(self, topic_name):
        """
        Deletes a Kafka topic

        Args:
            topic_name (str): The name of the topic to be deleted

        Returns:
            dict: Response JSON
        """
        url = f"{self.url}/topics/{topic_name}"
        response = requests.delete(url, auth=(self.user, self.password))
        return response.json()

    def list_topics(self):
        """
        Lists all Kafka topics

        Returns:
            dict: Response JSON
        """
        url = f"{self.url}/topics"
        response = requests.get(url, auth=(self.user, self.password))
        return response.json()

def usage():
    """
    Prints usage information for the script
    """
    print("Usage:")
    print("python kafka_topic_manager.py <environment> <command> [<topic_name>]")
    print("<environment>: The Kafka environment (e.g., dev, stage)")
    print("<command>: create / delete / list")
    print("<topic_name>: Required for delete command")


def main():
    """
    Main function - starting point of the script
    """
    if len(sys.argv) < 3:
        usage()
        sys.exit(1)

    env = sys.argv[1]
    command = sys.argv[2]
    manager = KafkaTopicManager(env)

    if command == "create":
        if len(sys.argv) < 5:
            print("Please provide topic_name, partitions, and replication_factor")
            usage()
            sys.exit(1)
        topic_name = sys.argv[3]
        partitions = int(sys.argv[4])
        replication_factor = int(sys.argv[5])
        response = manager.create_topic(topic_name, partitions, replication_factor)
        print(json.dumps(response, indent=4))

    elif command == "delete":
        if len(sys.argv) < 4:
            print("Please provide topic_name")
            usage()
            sys.exit(1)
        topic_name = sys.argv[3]
        response = manager.delete_topic(topic_name)
        print(json.dumps(response, indent=4))

    elif command == "list":
        response = manager.list_topics()
        print(json.dumps(response, indent=4))

    else:
        print(f"Invalid command: {command}")
        usage()
        sys.exit(1)

if __name__ == "__main__":
    main()
