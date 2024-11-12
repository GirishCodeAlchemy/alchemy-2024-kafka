import json
from datetime import datetime

from confluent_kafka import (
    OFFSET_INVALID,
    Consumer,
    IsolationLevel,
    KafkaException,
    TopicPartition,
)
from confluent_kafka.admin import AdminClient, OffsetSpec
from tabulate import tabulate

class KafkaTopicConsumer:
    def __init__(self, config_file, topic, group_id, auto_offset="earliest"):
        # Load Kafka configuration from a JSON file
        with open(config_file, 'r') as file:
            self.config = json.load(file)

        self.admin_client = AdminClient(self.config)
        # Set the group ID in the configuration
        self.config['group.id'] = group_id
        self.config['auto.offset.reset'] = offset

        # Initialize the Kafka consumer
        self.consumer = Consumer(self.config)
        self.topic = topic
        self.display_partition_offsets_and_lag()

    def display_partition_offsets_and_lag(self):
        metadata = self.consumer.list_topics(topic, timeout=10)
        if metadata.topics[topic].error is not None:
            raise KafkaException(metadata.topics[topic].error)

        # Construct TopicPartition list of partitions to query
        partitions = [TopicPartition(topic, p) for p in metadata.topics[topic].partitions]

        topic_partition_offsets = {}
        for each_partitions in partitions:
            topic_partition_offsets[each_partitions] = OffsetSpec.max_timestamp()

        futmap = self.admin_client.list_offsets(topic_partition_offsets, isolation_level=IsolationLevel.READ_COMMITTED, request_timeout=30)

        topic_latest_offset = {}
        for partition, fut in futmap.items():
            try:
                result = fut.result()
                human_readable_timestamp = (
                    datetime.fromtimestamp(result.timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
                    if result.timestamp != -1 else "N/A"
                )
                topic_latest_offset[partition.partition] = [result.offset+1, human_readable_timestamp]
            except KafkaException as e:
                print(f"Error retrieving offsets for {partition.topic} partition {partition.partition}: {e}")

        # Query committed offsets for this group and the given partitions
        committed = self.consumer.committed(partitions, timeout=10)

        table_data = []
        for partition in committed:
            # Get the partitions low and high watermark offsets.
            (lo, hi) = self.consumer.get_watermark_offsets(partition, timeout=10, cached=False)

            if partition.offset == OFFSET_INVALID:
                offset = "-"
            else:
                offset = "%d" % (partition.offset)

            if hi < 0:
                lag = "no hwmark"  # Unlikely
            elif partition.offset < 0:
                # No committed offset, show total message count as lag.
                # The actual message count may be lower due to compaction
                # and record deletions.
                lag = "%d" % (hi - lo)
            else:
                lag = "%d" % (hi - partition.offset)

            table_data.append([
                partition.topic,
                partition.partition,
                offset,
                lag,
                topic_latest_offset[partition.partition][0],
                topic_latest_offset[partition.partition][1]
            ])

        print(tabulate(table_data, headers=["Topic", "Partition", "Consumer Offset", "Lag", "Topic Offset", "Timestamp"], tablefmt="grid"))


    def get_partitions(self):
        # Get metadata for the topic to retrieve partition information
        metadata = self.consumer.list_topics(self.topic)
        return list(metadata.topics[self.topic].partitions.keys())

    def consume_messages(self, timeout=1.0):
        # Subscribe to the specified topic
        self.consumer.subscribe([self.topic])

        print("Starting to consume messages...")
        try:
            while True:
                msg = self.consumer.poll(timeout)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaException._PARTITION_EOF:
                        print(f"Reached end of partition {msg.partition()}")
                    else:
                        print(f"Error: {msg.error()}")
                    continue

                # Display message details
                _, timestamp = msg.timestamp()
                human_readable_timestamp = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
                print(f"Received message: {msg.value().decode('utf-8')}")
                print(f"Topic: {msg.topic()}, Partition: {msg.partition()}, Offset: {msg.offset()}, Timestamp: {human_readable_timestamp}")

        except KeyboardInterrupt:
            print("Stopped consuming.")
            self.display_partition_offsets_and_lag()
        finally:
            # Close the consumer to release resources
            self.consumer.close()


    def consume_from_offset(self, partition, offset, timeout=1.0):
        # Assign a specific partition and offset to start consuming from
        tp = TopicPartition(self.topic, partition, offset)
        self.consumer.assign([tp])

        print(f"Starting to consume messages from {self.topic} partition {partition} at offset {offset}...")
        try:
            while True:
                msg = self.consumer.poll(timeout)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaException._PARTITION_EOF:
                        print(f"Reached end of partition {msg.partition()}")
                    else:
                        print(f"Error: {msg.error()}")
                    continue

                # Display message details
                timestamp_type, timestamp = msg.timestamp()
                human_readable_timestamp = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
                print(f"Received message: {msg.value().decode('utf-8')}")
                print(f"Topic: {msg.topic()}, Partition: {msg.partition()}, Offset: {msg.offset()}, Timestamp: {human_readable_timestamp}")

        except KeyboardInterrupt:
            print("Stopped consuming.")
        finally:
            # Close the consumer to release resources
            self.consumer.close()


# Usage example
if __name__ == "__main__":
    # Initialize consumer with the configuration file, topic name, and group ID
    config_file = "config.json"
    topic = "topic1"
    group_id = "group1"

    auto_offset = "earliest" # Start from the beginning if no previous offset exists
    consumer = KafkaTopicConsumer(config_file, topic, group_id, auto_offset)

    # Press enter to start the consuming message
    input("Press Enter to start consuming messages...")
    # Start consuming messages
    consumer.consume_messages()
    # consumer.consume_from_offset(partition=1, offset=2350)