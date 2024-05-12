# Achemy Kafka

---

## Requirements

- Python 3.x
- requests
- dotenv

## How to Use

1. Install the required dependencies by running:

```bash
pip install -r requirements.txt
```

2. Set up your environment variables for authentication:
   default is set to empty

```bash
export CACERT=/path/to/certificate.crt
export CA_KEY=/path/to/key.key
export CA_CER=/path/to/ca_certificate.crt
```

3. Run the script with the desired command and parameters:

---

# Kafka Connector Management Commands

Below are the commands to manage Kafka connectors using the `kafka_connector` script:

## List Connectors

This command lists all connectors in the dev environment.

```bash
./kafka_connector dev list
```

## Get Connector Configuration

This command retrieves the configuration of the simple-connector in the dev environment.

```bash
./kafka_connector dev get simple-connector
```

## Get Connector Status

This command retrieves the status of the simple-connector in the dev environment.

```bash
./kafka_connector dev status simple-connector
```

## Create Connector

This command creates a new connector named simple-connector with the specified configuration in the dev environment.

```bash
./kafka_connector dev create '{"name":"simple-connector","config":{"connector.class":"com.github.jcustenborder.kafka.connect.spooldir.SpoolDirJsonSourceConnector","task.max":"1","topic":"test-topic","input.path":"/home/appuser/connect-test/input","input.file.pattern":"sample.txt","error.path":"/home/appuser/connect-test/failure","finished.path":"/home/appuser/connect-test/success","schema.generation.enabled":true,"value.converter":"org.apache.kafka.connect.json.JsonConverter"}}'
```

## Update Connector Configuration

This command updates the configuration of the simple-connector in the dev environment.

```bash
./kafka_connector dev update simple-connector '{"connector.class":"com.github.jcustenborder.kafka.connect.spooldir.SpoolDirJsonSourceConnector","task.max":"1","topic":"test-topic","input.path":"/home/appuser/connect-test/input","input.file.pattern":"sample.txt","error.path":"/home/appuser/connect-test/failure","finished.path":"/home/appuser/connect-test/success","schema.generation.enabled":true,"value.converter":"org.apache.kafka.connect.json.JsonConverter"}'
```
