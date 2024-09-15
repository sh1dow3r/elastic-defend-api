
# elastic-defend-api

Elastic Defend API is a Python-based CLI tool designed to interact with the Elasticsearch Defend API. It enables you to perform various operations on endpoint agents, such as executing commands, uploading and downloading files, checking the status of actions, and listing endpoints.

## Features

- **Execute Commands**: Remotely execute commands on endpoint agents.
- **File Upload**: Upload files to endpoint agents.
- **File Download**: Download files from endpoint agents (automatically handles polling for action completion).
- **Check Status**: Check the status of an action using the Action ID.
- **List Endpoints**: List all available endpoints with relevant metadata (Hostname, OS, and Agent ID).

## Requirements

- Python 3.9 or later
- Dependencies (install via pip):
  - requests
  - requests-toolbelt
  - colorama

## Installation

Clone the repository and install the required dependencies.

```bash
git clone https://github.com/sh1dow3r/elastic-defend-api
cd elastic-defend-api
pip install -r requirements.txt
```

## Configuration

You need to edit the `config.json` file in the root of the project. The file should have the following structure:

```json
{
  "cluster01": {
    "username": "your-username",
    "password": "your-password",
    "base_url": "https://your-kibana-url.com",
    "endpoint_ids": [
      "endpoint-id-1",
      "endpoint-id-2"
    ]
  }
}
```

You can define multiple clusters and switch between them in your CLI operations.

## Usage

You can use elastic-defend-api via the command line. Below are the available operations:

### 1. Execute Command

Execute a remote command on an endpoint.

```bash
python3 elastic-defend-api.py -c cluster01 -o execute --command "whoami"
```

### 2. File Upload

Upload a file to an endpoint.

```bash
python3 elastic-defend-api.py -c cluster01 -o file_upload --local_file "/path/to/file.txt"
```

### 3. File Download

Download a file from an endpoint.

```bash
python3 elastic-defend-api.py -c cluster01 -o file_download --remote_file "C:/path/to/remote/file.txt"
```

### 4. Check Status

Check the status of an action using the Action ID.

```bash
python3 elastic-defend-api.py -c cluster01 -o check_status --action_id "action-id-here"
```

### 5. List Endpoints

List all available endpoints with their metadata.

```bash
python3 elastic-defend-api.py -c cluster01 -o list_endpoints
```

## Logging

elastic-defend-api logs operations and results to the console. You can easily track the progress and any issues by following the logs.

## Contributing

Contributions are welcome! If you'd like to improve this project, feel free to submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
