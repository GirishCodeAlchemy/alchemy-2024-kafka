import os

import requests
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory(os.getcwd(), 'index.html')

@app.route('/trigger-pipeline', methods=['POST'])
def trigger_pipeline():
    data = request.json
    required_keys = ['consumers', 'connectors', 'idempotent', 'ksql', 'user', 'group', 'read_only', 'topics', 'pattern_type', 'env', 'requested_by', 'option']
    if not all(key in data for key in required_keys):
        return jsonify({'error': 'Missing required parameters'}), 400

    # GitLab project details
    gitlab_project_id = 'your_project_id'
    gitlab_pipeline_trigger_url = f'https://gitlab.com/api/v4/projects/{gitlab_project_id}/trigger/pipeline'
    gitlab_trigger_token = 'your_trigger_token'

    # Prepare the payload for the GitLab pipeline
    payload = {
        'token': gitlab_trigger_token,
        'ref': 'main',  # or any other branch you want to trigger the pipeline on
        'variables[CONSUMERS]': ','.join(data['consumers']),
        'variables[CONNECTORS]': ','.join(data['connectors']),
        'variables[IDEMPOTENT]': str(data['idempotent']),
        'variables[KSQL]': str(data['ksql']),
        'variables[USER]': data['user'],
        'variables[GROUP]': data['group'],
        'variables[READ_ONLY]': str(data['read_only']),
        'variables[TOPICS]': ','.join(data['topics']),
        'variables[PATTERN_TYPE]': data['pattern_type'],
        'variables[ENV]': data['env'],
        'variables[TRIGGERED_BY]': data['requested_by'],
        'variable[OPTION]':data['option']
    }
    print(payload)
    response = requests.post(gitlab_pipeline_trigger_url, data=payload)

    if response.status_code == 201:
        return jsonify({'status': 'RBAC creation is Submitted'}), 201
    else:
        return jsonify({'error': 'Failed to Create RBAC', 'details': response.json()}), response.status_code

if __name__ == '__main__':
    app.run(debug=True)
