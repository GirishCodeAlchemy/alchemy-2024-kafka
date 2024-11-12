import json
from datetime import datetime

from confluent_kafka import IsolationLevel, KafkaException, Producer, TopicPartition
from confluent_kafka.admin import AdminClient, OffsetSpec
from tabulate import tabulate


class KafkaTopicProducer:
    def __init__(self, config_file, topic):
        # Load Kafka configuration from a JSON file
        with open(config_file, 'r') as file:
            self.config = json.load(file)

        # Initialize the Kafka producer with the configuration
        self.producer = Producer(self.config)
        self.topic = topic
        self.admin_client = AdminClient(self.config)
        # Get the number of partitions for the topic
        topic_metadata = self.producer.list_topics(self.topic)
        self.num_partitions = len(topic_metadata.topics[self.topic].partitions)

        if self.num_partitions < 1:
            raise ValueError("The topic must have at least one partition.")

        self.partition_index = 0
        print("\nCurrent Offsets:")
        self.display_partition_offsets()

    def display_partition_offsets(self, offset_spec="MAX_TIMESTAMP"):
        """
        Displays the offsets of the topic's partitions based on the specified offset spec.
        """
        topic_partition_offsets = {}
        isolation_level = IsolationLevel.READ_COMMITTED

        # Define the offset spec for each partition
        for partition in range(self.num_partitions):
            topic_partition = TopicPartition(self.topic, partition)

            # Set the appropriate offset spec
            if offset_spec == "EARLIEST":
                topic_partition_offsets[topic_partition] = OffsetSpec.earliest()
            elif offset_spec == "LATEST":
                topic_partition_offsets[topic_partition] = OffsetSpec.latest()
            elif offset_spec == "MAX_TIMESTAMP":
                topic_partition_offsets[topic_partition] = OffsetSpec.max_timestamp()
            else:
                raise ValueError("Invalid offset_spec, must be EARLIEST, LATEST, or MAX_TIMESTAMP")

        # Request offsets from the broker
        futmap = self.admin_client.list_offsets(topic_partition_offsets, isolation_level=isolation_level, request_timeout=30)
        table_data = []

        for partition, fut in futmap.items():
            try:
                result = fut.result()
                human_readable_timestamp = (
                    datetime.fromtimestamp(result.timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
                    if result.timestamp != -1 else "N/A"
                )
                table_data.append([
                    partition.topic, partition.partition, result.offset, human_readable_timestamp
                ])
            except KafkaException as e:
                print(f"Error retrieving offsets for {partition.topic} partition {partition.partition}: {e}")

        # Display partition offset details in table format
        print(tabulate(table_data, headers=["Topic", "Partition", "Offset", "Timestamp"], tablefmt="grid"))

    def delivery_report(self, err, msg):
        # Callback for delivery reports
        if err is not None:
            print(f"Message delivery failed: {err}")
        else:
            print(f"Message delivered to {msg.topic()} in partition [{msg.partition()}] at offset {msg.offset()}")

    def send_message(self, message, partition=None):
        json_data = json.dumps(message)
        if partition is None:
            self.producer.produce(
                self.topic,
                json_data,
                callback=self.delivery_report
            )
        else:
            if partition < 0 or partition >= self.num_partitions:
                raise ValueError("Invalid partition number.")
            self.producer.produce(
                self.topic,
                json_data,
                partition=partition,
                callback=self.delivery_report
            )

        self.producer.poll(0)

    def send_message_round_robin(self, message):

        json_data = json.dumps(message)

        # Set the partition number in a round-robin fashion
        partition = self.partition_index
        self.partition_index = (self.partition_index + 1) % self.num_partitions

        # Send the message to the specified partition
        self.producer.produce(
            self.topic,
            json_data,
            partition=partition,
            callback=self.delivery_report
        )
        self.producer.poll(0)

    def flush(self):
        # Ensure all messages are sent before exiting
        self.producer.flush()


# Usage example
if __name__ == "__main__":
    # Initialize producer with the configuration file and topic name
    config_file = "config.json"
    topic = "topic1"

    producer = KafkaProducer(config_file, topic)

    # Send messages to default partitions
    for i in range(10):
        # Construct the message payload
        message = {"key": i, "value": f"Test message {i}"}
        producer.send_message(message)

    # Flush to ensure all messages are sent
    producer.flush()
    print("\nLatest offsets:")
    producer.display_partition_offsets()

    # Send messages in a round-robin fashion across partitions
    for i in range(10):
        message = {"key": i, "value": f"Test message {i}"}
        producer.send_message_round_robin(message)
    producer.flush()
    print("\nLatest offsets:")
    producer.display_partition_offsets()

    # Send messages to specific partitions
    for i in range(10):
        # Construct the message payload
        message = {"key": i, "value": f"Test message {i}"}
        producer.send_message(message, partition=1)
    producer.flush()
    print("\nLatest offsets:")
    producer.display_partition_offsets()