# Use the official Confluent Kafka Connect image as base
FROM confluentinc/cp-kafka-connect:7.3.0

# List of plugins to install
ARG KAFKA_CONNECT_PLUGINS="installjcustenborder/kafka-connect-spooldir:latest \
    debezium/debezium-connector-mysql:latest \
    debezium/debezium-connector-postgres:latest \
    debezium/debezium-connector-sqlserver:latest \
    confluentinc/kafka-connect-elasticsearch:latest \
    confluentinc/kafka-connect-spooldir:latest\
    installjcustenborder/kafka-connect-spooldir:1.0.31\
    confluentinc/kafka-connect-jdbc:latest \
    confluentinc/kafka-connect-hdfs:latest \
    confluentinc/kafka-connect-s3:latest \
    confluentinc/kafka-connect-aws-cloudwatch:latest \
    confluentinc/kafka-connect-datagen:latest"

# Install each plugin individually
RUN for plugin in $KAFKA_CONNECT_PLUGINS; do confluent-hub install --no-prompt $plugin; done

# Set up any additional configurations or adjustments here if needed
# For example, you can copy configuration files into the image or set environment variables
COPY plugins/ /usr/share/confluent-hub-components/.

RUN mkdir -p /home/appuser/connect-test/input /home/appuser/connect-test/success /home/appuser/connect-test/failure

# Optionally, expose any ports needed for communication with Kafka or other services

# Command to start Kafka Connect when the container starts (you may adjust it based on your needs)
# CMD ["bash", "-c", "confluent local services start connect"]

