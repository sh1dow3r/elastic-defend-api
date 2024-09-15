# es_defend.py

import argparse
import os
from utils import load_config, make_post_request, make_get_request, make_get_request_for_file
from colorama import Fore, Style
import logging
import requests
from requests_toolbelt import MultipartEncoder
import json
import time

# Execute command on an endpoint
def execute_command(cluster_name, command, comment, timeout=600):
    try:
        config = load_config(cluster_name)
        url = f"{config['base_url']}/api/endpoint/action/execute"
        payload = {
            "endpoint_ids": config['endpoint_ids'],
            "parameters": {
                "command": command,
                "timeout": timeout
            },
            "comment": str(comment)
        }

        logging.info(f"Executing command with payload: {payload}")
        action_id = make_post_request(url, config['username'], config['password'], payload).get("action", None)
        if action_id:
            print(f"{Fore.GREEN}Command executed successfully. Action ID: {action_id}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Failed to retrieve Action ID.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error executing command: {e}{Style.RESET_ALL}")

# Upload a file to an endpoint using MultipartEncoder
def file_upload(cluster_name, file_path):
    try:
        config = load_config(cluster_name)
        url = f"{config['base_url']}/api/endpoint/action/upload"
        
        if not os.path.isfile(file_path):
            print(f"{Fore.RED}File not found: {file_path}{Style.RESET_ALL}")
            return

        encoder = MultipartEncoder(
            fields={
                'file': (os.path.basename(file_path), open(file_path, 'rb'), 'application/octet-stream'),
                'endpoint_ids': json.dumps(config['endpoint_ids'])
            }
        )

        headers = {
            'kbn-xsrf': 'true',
            'Content-Type': encoder.content_type
        }

        response = requests.post(url, auth=(config['username'], config['password']), data=encoder, headers=headers, verify=False)
        response.raise_for_status()
        
        action_id = response.json().get("action", None)
        if action_id:
            print(f"{Fore.GREEN}File uploaded successfully. Action ID: {action_id}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Failed to retrieve Action ID.{Style.RESET_ALL}")
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}Error uploading file: {e}{Style.RESET_ALL}")

def get_endpoint_details(cluster_name, agent_id):
    try:
        config = load_config(cluster_name)
        url = f"{config['base_url']}/api/endpoint/metadata/{agent_id}"
        response = make_get_request(url, config['username'], config['password'])
        return response.get('metadata', [])
        
    except Exception as e:
        print(f"{Fore.RED}Error listing endpoints: {e}{Style.RESET_ALL}")

# file download function
def file_download(cluster_name, remote_file, polling_interval=15, max_retries=40):
    try:
        config = load_config(cluster_name)
        url = f"{config['base_url']}/api/endpoint/action/get_file"
        
        payload = {
            "endpoint_ids": config['endpoint_ids'],
            "parameters": {
                "path": remote_file
            },
            "comment": "File download request"
        }
        
        logging.info(f"Preparing file download with payload: {payload}")
        response = make_post_request(url, config['username'], config['password'], payload)

        action_id = response.get("action", None)
        if not action_id:
            print(f"{Fore.RED}Failed to retrieve Action ID for file download.{Style.RESET_ALL}")
            return

        # Polling for action completion
        for attempt in range(max_retries):
            print(f"Polling action status (Attempt {attempt + 1}/{max_retries})...")
            status_response = check_status(cluster_name, action_id)
            status = status_response.get('status', 'pending')

            if status == 'successful':
                endpoint_id = config['endpoint_ids'][0]
                
                # Construct download URL using action_id and endpoint_id
                download_url = f"{config['base_url']}/api/endpoint/action/{action_id}/file/{action_id}.{endpoint_id}/download"
                
                # Use the new function to download the file (handle it as binary data)
                download_response = make_get_request_for_file(download_url, config['username'], config['password'])
                
                # Check if the download was successful
                if download_response.status_code != 200:
                    print(f"{Fore.RED}Failed to download file. Status code: {download_response.status_code}{Style.RESET_ALL}")
                    return
                
                # Create output directory if it doesn't exist
                output_dir = "es_defend_output"
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)

                #Get hostname 
                endpoint_details = get_endpoint_details(cluster_name,config['endpoint_ids'][0])
                hostname = endpoint_details['host']['hostname']

                # Save file as .zip (assuming it will always be a zip file)
                file_name = f"{hostname}_{os.path.basename(remote_file)}".replace("/","_").replace("\\", "_").strip(":  ")
                output_path = os.path.join(output_dir, file_name)

                # Write the binary content of the file
                with open(output_path, "wb") as file:
                    file.write(download_response.content)

                print(f"{Fore.GREEN}File downloaded successfully to '{output_path}'{Style.RESET_ALL}")
                return
            elif status == 'failed':
                print(f"{Fore.RED}File download action failed.{Style.RESET_ALL}")
                return

            time.sleep(polling_interval)

        print(f"{Fore.RED}File download action did not complete within the allotted time.{Style.RESET_ALL}")

    except Exception as e:
        print(f"{Fore.RED}Error downloading file: {e}{Style.RESET_ALL}")
        logging.error(f"Error details: {str(e)}", exc_info=True)


# Check the status of an action
def check_status(cluster_name, action_id):
    try:
        config = load_config(cluster_name)
        url = f"{config['base_url']}/api/endpoint/action/{action_id}"
        response = make_get_request(url, config['username'], config['password'])
        action_data = response.get('data', {})
        print(f"{Fore.CYAN}{action_data}{Style.RESET_ALL}")
        return action_data  # Return the full action data
    except Exception as e:
        print(f"{Fore.RED}Error checking status: {e}{Style.RESET_ALL}")
        return {}

# List all endpoints with agent_id and a pageSize of 10000
def list_endpoints(cluster_name):
    try:
        config = load_config(cluster_name)
        url = f"{config['base_url']}/api/endpoint/metadata?pageSize=10000"
        response = make_get_request(url, config['username'], config['password'])
        
        for endpoint in response.get('data', []):
            agent_id = endpoint['metadata']['elastic']['agent']['id']
            hostname = endpoint['metadata']['host']['hostname']
            os_name = endpoint['metadata']['host']['os']['name']
            print(f"{Fore.CYAN}Hostname: {hostname}, OS: {os_name}, Agent ID: {agent_id}{Style.RESET_ALL}")
            
    except Exception as e:
        print(f"{Fore.RED}Error listing endpoints: {e}{Style.RESET_ALL}")

# Argument parser for handling CLI inputs
def parse_args():
    parser = argparse.ArgumentParser(description="CLI tool for managing ES Defend operations.")
    parser.add_argument('-c', '--cluster_name', required=True, help="Cluster name (cluster01, cluster02, cluster03)")
    parser.add_argument('-o', '--operation', required=True, choices=['execute', 'file_upload', 'file_download_prep', 'file_download', 'check_status', 'list_endpoints'], help="Operation to perform")

    parser.add_argument('--command', help="Command to execute (for 'execute' operation)")
    parser.add_argument('--comment', type=str, default="ES_Defend Request", help="comment to add to request (for 'execute' operation)")
    parser.add_argument('--timeout', type=int, default=600, help="Timeout for the command (default: 600)")
    parser.add_argument('--local_file', help="Local file path for upload")
    parser.add_argument('--remote_file', help="Remote file path for file download prep")
    parser.add_argument('--action_id', help="Action ID for file download or status check")
    parser.add_argument('--output_id', help="Output ID for file download")

    return parser.parse_args()

# Main function to execute based on parsed arguments
def main():
    args = parse_args()

    if args.operation == "execute":
        if not args.command:
            print(f"{Fore.RED}Error: --command is required for execute operation{Style.RESET_ALL}")
            return
        execute_command(args.cluster_name, args.command, args.comment, args.timeout)

    elif args.operation == "file_upload":
        if not args.local_file:
            print(f"{Fore.RED}Error: --local_file is required for file_upload operation{Style.RESET_ALL}")
            return
        file_upload(args.cluster_name, args.local_file)

    elif args.operation == "file_download":
        if not args.remote_file:
            print(f"{Fore.RED}Error: --remote_file is required for file_download operation{Style.RESET_ALL}")
            return
        # Download the file by initiating and completing the request
        file_download(args.cluster_name, args.remote_file)

    elif args.operation == "check_status":
        if not args.action_id:
            print(f"{Fore.RED}Error: --action_id is required for check_status operation{Style.RESET_ALL}")
            return
        check_status(args.cluster_name, args.action_id)

    elif args.operation == "list_endpoints":
        list_endpoints(args.cluster_name)

if __name__ == '__main__':
    main()