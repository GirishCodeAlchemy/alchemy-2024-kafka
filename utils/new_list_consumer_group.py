from confluent_kafka.admin import AdminClient
from confluent_kafka import KafkaException

def get_consumers_for_topic(broker_url, topic_name, ca_cert, client_cert, client_key):
    """
    Fetch the list of consumer groups subscribed to a given Kafka topic using SSL certificates.
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
        consumer_groups = admin_client.list_consumer_groups()
        group_ids = [group[0] for group in consumer_groups]

        topic_consumers = []

        # Describe each group
        group_descriptions = admin_client.describe_consumer_groups(group_ids)
        for group_description in group_descriptions:
            for member in group_description.members:
                for topic, partitions in member.assignment.items():
                    if topic == topic_name:
                        topic_consumers.append(group_description.group_id)
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
