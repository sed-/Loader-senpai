import os
import requests
from pathlib import Path
import time
import psutil  # Import psutil for process management

GITHUB_API_URL = "https://api.github.com"
REPO_OWNER = "sed-"
REPO_NAME = "Loader-senpai"

# Define the current directory as the current working directory
CURRENT_DIR = Path.cwd()

# List of files to ignore if they exist locally
FILES_TO_IGNORE = ["token.txt", "username.txt", "watched_anime.txt", "closeall.config"]

# Function to check if a process with a given PID is running using psutil
def is_process_running(pid):
    return psutil.pid_exists(pid)

# Function to terminate process based on PID in pid.txt using psutil
def terminate_process_from_pid():
    pid_file = CURRENT_DIR / 'pid.txt'
    if pid_file.exists():
        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            if is_process_running(pid):
                process = psutil.Process(pid)
                process.terminate()  # Gracefully terminate the process
                try:
                    process.wait(timeout=5)  # Wait up to 5 seconds for the process to terminate
                    print(f"Terminated process with PID {pid}")
                except psutil.TimeoutExpired:
                    print(f"Process with PID {pid} did not terminate in time; attempting to kill it")
                    process.kill()  # Forcefully kill the process
                    print(f"Killed process with PID {pid}")
            else:
                print(f"No running process found with PID {pid}")
        except ValueError:
            print("Invalid PID in pid.txt")
        except psutil.NoSuchProcess:
            print(f"No process found with PID {pid}")
        except psutil.AccessDenied:
            print(f"Permission denied when trying to terminate PID {pid}")
        except Exception as e:
            print(f"Error terminating process with PID {pid}: {e}")
    else:
        print("pid.txt not found; no process to terminate")

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

            # If the file is in FILES_TO_IGNORE and it exists locally, skip updating it
            if local_file_path.name in FILES_TO_IGNORE and local_file_path.exists():
                continue

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
    terminate_process_from_pid()
    update_repo()
