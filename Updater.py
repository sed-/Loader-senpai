import os
import requests
from pathlib import Path
import time

GITHUB_API_URL = "https://api.github.com"
REPO_OWNER = "sed-"
REPO_NAME = "Loader-senpai"

# Get the path of the current script
CURRENT_DIR = Path(os.path.dirname(os.path.realpath(__file__)))

# Helper to fetch files from GitHub
def fetch_remote_files():
    url = f"{GITHUB_API_URL}/repos/{REPO_OWNER}/{REPO_NAME}/commits"
    response = requests.get(url)
    response.raise_for_status()  # Ensure no error in fetching
    
    latest_commit = response.json()[0]
    tree_url = latest_commit['commit']['tree']['url'] + "?recursive=1"
    tree_response = requests.get(tree_url)
    tree_response.raise_for_status()
    
    file_list = tree_response.json().get('tree', [])
    return file_list

# Download and return the content of a remote file
def download_file_content(remote_file_path):
    raw_url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/{remote_file_path}"
    response = requests.get(raw_url)
    response.raise_for_status()
    return response.content

# Main update function
def update_repo():
    remote_files = fetch_remote_files()
    added_files = 0  # Track the number of added files
    updated_files = 0  # Track the number of updated files

    for file_data in remote_files:
        if file_data['type'] == 'blob':
            remote_file_path = file_data['path']
            local_file_path = CURRENT_DIR / remote_file_path
            
            # Download the remote file content
            remote_file_content = download_file_content(remote_file_path)

            # Check if the local file exists
            if local_file_path.exists():
                # Read the local file content
                with open(local_file_path, 'rb') as local_file:
                    local_file_content = local_file.read()
                
                # Compare local and remote file content
                if local_file_content == remote_file_content:
                    continue  # No changes, skip
                
                # If file content is different, it's an update
                print(f"Updated: {local_file_path.name}")
                updated_files += 1

            else:
                # If file doesn't exist, it's a new file
                print(f"Added: {local_file_path.name}")
                added_files += 1

            # Write the new or updated content to the file
            local_file_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure directories exist
            with open(local_file_path, 'wb') as local_file:
                local_file.write(remote_file_content)

    # Summary of added and updated files
    print(f"\n{added_files} file(s) were added")
    print(f"{updated_files} file(s) were updated")

    # Pause for 12 seconds before exiting
    time.sleep(12)

if __name__ == "__main__":
    update_repo()
