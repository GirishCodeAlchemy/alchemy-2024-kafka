kafkactl create topics connect_configs
kafkactl create topic connect_configs
kafkactl create topic connect_statuses
kafkactl alter topic connect_statuses -c cleanup.policy=compact