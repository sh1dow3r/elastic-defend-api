# utils.py

import json
import logging
import requests
from requests.auth import HTTPBasicAuth
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

# Disable SSL warnings
requests.packages.urllib3.disable_warnings()

# Load the configuration for a specific cluster
def load_config(cluster_name='cluster01', config_file='config.json'):
    try:
        with open(config_file, 'r') as file:
            config = json.load(file)
        
        if cluster_name not in config:
            raise ValueError(f"Cluster {cluster_name} not found in config.json")
        
        log.info(f"Configuration loaded for cluster: {Fore.CYAN}{cluster_name}{Style.RESET_ALL}")
        return config[cluster_name]
    except (FileNotFoundError, json.JSONDecodeError) as e:
        log.error(f"{Fore.RED}Failed to load configuration: {e}")
        raise

# Helper function to make authenticated POST requests
def make_post_request(url, username, password, data):
    try:
        headers = {
            'kbn-xsrf': 'true'
        }
        
        log.info(f"Sending POST request to {url} with data: {data}")
        response = requests.post(url, auth=HTTPBasicAuth(username, password), json=data, headers=headers, verify=False)
        response.raise_for_status()
        log.info(f"{Fore.GREEN}POST request successful for URL: {url}{Style.RESET_ALL}")
        return response.json()
    except requests.exceptions.RequestException as e:
        log.error(f"{Fore.RED}POST request failed for {url}: {e}{Style.RESET_ALL}")
        raise

# Helper function to make authenticated GET requests
def make_get_request(url, username, password):
    try:
        response = requests.get(url, auth=HTTPBasicAuth(username, password), verify=False)
        response.raise_for_status()
        log.info(f"{Fore.GREEN}GET request successful for URL: {url}{Style.RESET_ALL}")
        return response.json()
    except requests.exceptions.RequestException as e:
        log.error(f"{Fore.RED}GET request failed for {url}: {e}{Style.RESET_ALL}")
        raise

# Helper function to make authenticated GET requests for files (binary data)
def make_get_request_for_file(url, username, password):
    try:
        # Make a GET request without parsing the response as JSON
        response = requests.get(url, auth=HTTPBasicAuth(username, password), verify=False)
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
        
        logging.info(f"{Fore.GREEN}GET request successful for URL: {url}{Style.RESET_ALL}")
        return response  # Return the raw response to handle binary data
    except requests.exceptions.RequestException as e:
        logging.error(f"{Fore.RED}GET request failed for {url}: {e}{Style.RESET_ALL}")
        raise
