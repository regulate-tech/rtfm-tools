# github-pages-local.py

# 1. makes a local copy of a list of GitHub repositories in repos.csv
# 2. runs the github pages workflow to create a fresh static website
# 3. finds the github pages artifact and downloads it
# 4. extracts the GitHub Pages artifact for local web serving
# 5. to test go to artifact directory and serve with "python -m http.server"

# NB the terminal must be logged in to GitHub with gh

#!/usr/bin/env python3

import csv
import os
import json
import time
import subprocess
import sys
import tarfile
from datetime import datetime


# Generic utility functions for file and directory operations
def run_command(command, cwd=None):
    """
    Run a shell command and return its output.
    Exits the script if the command fails.
    """
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, check=True,
                                cwd=cwd, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(command)}", file=sys.stderr)
        print(f"Stdout: {e.stdout}", file=sys.stderr)
        print(f"Stderr: {e.stderr}", file=sys.stderr)
        sys.exit(1)

# Uses a shell function to retrieve the workflow run ID for GitHub Pages deployment
def get_pages_workflow_run_id(repo_name):
    command = [
        "gh",
        "run",
        "list",
        "--workflow=pages-build-deployment",
        "--limit=1",
        "--json",
        "databaseId"
    ]
    try:
        process = subprocess.run(command, capture_output=True, text=True, check=True)
        json_output = json.loads(process.stdout)
        database_id = json_output[0]["databaseId"]
        return database_id
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None
    except IndexError as e:
        print(f"Error indexing the result: {e}")
        return None

# Creates local copies of repositories by cloning or updating them
def clone_or_update_repo(repo_url, target_dir):
    """
    Clone the repository if it does not exist; otherwise, pull the latest changes.
    """
    if os.path.isdir(target_dir):
        print(f"Repository already exists in '{target_dir}'. Pulling latest changes...")
        run_command(["git", "pull"], cwd=target_dir)
    else:
        print(f"Cloning repository '{repo_url}' into '{target_dir}'...")
        run_command(["git", "clone", repo_url, target_dir])

# Triggers GitHub Pages workflow as artifacts are deleted after 24 hours    
def trigger_pages_workflow(repo_dir):
    """
    Triggers the GitHub Pages workflow by making a commit.
    Returns True if successful, False otherwise.
    """
    try:
        original_cwd = os.getcwd()
        os.chdir(repo_dir)

        print("Triggering GitHub Pages workflow via commit...")

        # Create a timestamp using Python's datetime
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        commit_message = f"trigger: rebuild pages {timestamp}"

        # Create an empty commit to trigger the workflow
        run_command(["git", "commit", "--allow-empty", "-m", commit_message])
        run_command(["git", "push"])

        # Wait for 60 seconds to allow the workflow to start
        print("Waiting 60 seconds for workflow to initialize...")
        time.sleep(60)

        # Get the latest run ID
        latest_run = get_pages_workflow_run_id(repo_dir)
        if not latest_run:
            print("Failed to get workflow run ID")
            return False

        # Wait for workflow to complete using the run ID
        print("Waiting for workflow to complete...")
        check_workflow = [
            "gh",
            "run",
            "watch",
            str(latest_run)
        ]

        run_command(check_workflow)

        os.chdir(original_cwd)
        return True

    except Exception as e:
        print(f"Error triggering workflow: {e}")
        os.chdir(original_cwd)
        return False

# Pulls the static pages by getting the latest workflow run ID and downloading the artifact
def download_artifact(repo_dir, artifact_dir, repo_name):
    # NB We need to be in the repository directory to download the artifact  
    try:
        original_cwd = os.getcwd() #save original working directory.
        os.chdir(repo_dir) #change working directory to repo directory.

        print("Starting artifact download process...")

        # Get the latest run ID from GitHub Actions workflow
        latest_run = get_pages_workflow_run_id(repo_name)
        print(f"Latest run ID: {latest_run}")

        # Clean up existing artifact directory and recreate it
        if os.path.exists("artifact"):
            print("Removing existing artifact directory...")
            for file in os.listdir("artifact"):
                file_path = os.path.join("artifact", file)
                if os.path.isfile(file_path):
                    os.remove(file_path)

        # Ensure the artifact directory exists
        os.makedirs("artifact", exist_ok=True)
        print(f"Artifact directory created/verified: {artifact_dir}")

        # Download the artifact using the run ID
        download_cmd = [
            "gh",
            "run",
            "download",
            str(latest_run), # string function needed
            "--name",
            "github-pages",
            "--dir",
            "artifact"
        ]       

        result = subprocess.run(download_cmd, shell=False, capture_output=True, text=True)

        print(f"We have a result: {result}")

        current_path = os.getcwd()
        print(f"\nCurrent directory path: {current_path}")
        print("Current directory contents:")
        for file in os.listdir('.'):
            print(f"- {file}")

        print(f"Command stdout: {result.stdout}")
        print(f"Command stderr: {result.stderr}")
        
        os.chdir(original_cwd) #change working directory back to original.
        
        if result.returncode != 0:
            print(f"Error downloading artifact (return code: {result.returncode})")
            print(result.stderr)
            return False

        print(f"Successfully downloaded github-pages artifact to {artifact_dir}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        print(f"Command output: {e.output}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        print(f"Error type: {type(e)}")
        return False

# Extract the tar file to create a local website copy
def extract_artifact(artifact_dir):
    try:
        original_cwd = os.getcwd() #save original working directory.
        os.chdir(artifact_dir) #change working directory to repo directory.

        # Add directory listing for debugging
        current_path = os.getcwd()
        print(f"\nCurrent directory path: {current_path}")
        print("Current directory contents:")
        for file in os.listdir('.'):
            print(f"- {file}")

        print("Extracting artifact.tar...")
        with tarfile.open('artifact.tar', 'r') as tar:
            tar.extractall(path='.')
        print("Extraction completed successfully")
        os.chdir(original_cwd) #change working directory back to original.

    except Exception as e:
        print(f"Error extracting artifact.tar: {str(e)}")
        raise

# Main processing loop that does the work
def process_repo(repo_url, domain, base_dir):
    """
    Process a single repository:
    1. Clone or update the repo
    2. Trigger GitHub Pages workflow
    3. Download and extract the artifact producing the static site

    Returns:
        bool: True if all steps completed successfully, False otherwise
    """
    try:
        # Extract a friendly repository name from the URL
        repo_name = repo_url.rstrip("/").split("/")[-1]
        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]

        # Make a local copy of the GitHub repo
        repo_dir = os.path.join(base_dir, repo_name)
        print(f"Cloning/updating repository...")
        clone_or_update_repo(repo_url, repo_dir)

        # Trigger the GitHub Pages workflow and wait for completion
        print(f"Triggering GitHub Pages workflow...")
        if not trigger_pages_workflow(repo_dir):
            print("Failed to trigger GitHub Pages workflow")
            return False

        # Prepare a directory where the artifact will be downloaded and extracted
        artifact_dir = os.path.join(repo_dir, "artifact")
        os.makedirs(artifact_dir, exist_ok=True)

        # Download the artifact named "artifact.tar"
        print(f"Downloading artifact...")
        if not download_artifact(repo_dir, artifact_dir, repo_name):
            print("Failed to download artifact")
            return False

        # Extract the artifact file so we have a local website copy
        print(f"Extracting artifact...")
        extract_artifact(artifact_dir)

        print(f"Successfully processed repository: {repo_name}")
        return True

    except Exception as e:
        print(f"Error processing repository {repo_url}: {str(e)}")
        return False

# Main function checks local files and loops through the repos
def main():
    input_file = "repos.csv"  # CSV file with each row as: repo_url,domain
    base_dir = "repos"        # Directory where repositories will be cloned

    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    if not os.path.exists(input_file):
        print(f"Input file '{input_file}' not found.", file=sys.stderr)
        sys.exit(1)

    with open(input_file, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if not row or len(row) < 2:
                continue  # Skip empty lines or incomplete entries
            repo_url = row[0].strip()
            domain = row[1].strip()
            print(f"\nProcessing repository: {repo_url} for domain: {domain}")
            process_repo(repo_url, domain, base_dir)
            print("-" * 40)

if __name__ == "__main__":
    main()