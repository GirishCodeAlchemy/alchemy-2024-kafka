from confluent_kafka.admin import AdminClient
from confluent_kafka import KafkaException

def get_consumers_for_topic(broker_url, topic_name, ca_cert, client_cert, client_key):
    """
    Fetch the list of consumer groups subscribed to a given Kafka topic using SSL certificates.

    :param broker_url: Kafka broker URL
    :param topic_name: Kafka topic name
    :param ca_cert: Path to the CA certificate file
    :param client_cert: Path to the client certificate file
    :param client_key: Path to the client key file
    :return: List of consumer group IDs consuming the topic
    """
    admin_client = AdminClient({
        "bootstrap.servers": broker_url,
        "security.protocol": "SSL",
        "ssl.ca.location": ca_cert,
        "ssl.certificate.location": client_cert,
        "ssl.key.location": client_key
    })

    try:
        # Get all consumer groups
        consumer_groups = admin_client.list_groups().groups

        topic_consumers = []

        for group in consumer_groups:
            group_id = group["group"]

            # Describe the group to get topic information
            group_description = admin_client.describe_consumer_groups([group_id])
            for group_metadata in group_description:
                assignments = group_metadata.assignment
                for topic, partitions in assignments.items():
                    if topic == topic_name:
                        topic_consumers.append(group_id)
                        break

        return topic_consumers

    except KafkaException as e:
        print(f"Error fetching consumer groups: {e}")
        return []

# Example usage
if __name__ == "__main__":
    broker_url = "your.kafka.broker:9093"
    topic_name = "your_topic_name"
    ca_cert = "/path/to/ca-cert.pem"
    client_cert = "/path/to/client-cert.pem"
    client_key = "/path/to/client-key.pem"

    consumers = get_consumers_for_topic(broker_url, topic_name, ca_cert, client_cert, client_key)
    print(f"Consumers for topic '{topic_name}': {consumers}")
