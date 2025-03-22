# This script assumes that you have logged in to AWS from the command line in the terminal where you will run it.
# You will normally login with the command 'aws auth login' and then following prompts for various methods.

import subprocess
import sys

def check_and_create_s3_bucket(bucket_name, region="eu-north-1"):
    """
    Checks if an S3 bucket exists in the current AWS account and creates it if it doesn't.

    Args:
        bucket_name (str): The name of the S3 bucket.
        region (str): The AWS region to create the bucket in.

    Returns:
        tuple: A tuple containing the return code (0 for success, non-zero for failure) and
               a message indicating the result.
    """

    try:
        # Check if the bucket exists in the current account.
        subprocess.run(["aws", "s3api", "head-bucket", "--bucket", bucket_name], check=True, capture_output=True)
        return 0, f"Bucket '{bucket_name}' already exists in your account."

    except subprocess.CalledProcessError as e:
        if e.returncode == 404:  # Bucket doesn't exist.
            try:
                # Create the bucket.
                command = [
                    "aws",
                    "s3api",
                    "create-bucket",
                    "--bucket",
                    bucket_name,
                    "--region",
                    region,
                    "--create-bucket-configuration",
                    f"LocationConstraint={region}",
                ]
                subprocess.run(command, check=True, capture_output=True)
                return 0, f"Bucket '{bucket_name}' created successfully in {region}."
            except subprocess.CalledProcessError as create_error:
                return create_error.returncode, f"Error creating bucket '{bucket_name}' in {region}:\n{create_error.stderr}"
            except Exception as create_exception:
                return 1, f"An unexpected error occurred during bucket creation: {create_exception}"
        else: # other errors
            return e.returncode, f"Error checking bucket '{bucket_name}':\n{e.stderr}"
    except FileNotFoundError:
        return 1, "Error: AWS CLI not found. Make sure it's installed and in your PATH."
    except Exception as e:
        return 1, f"An unexpected error occured: {e}"

# Example Usage
if __name__ == "__main__":
    bucket_name = "your-unique-bucket-name"  # Replace with your desired bucket name
    return_code, message = check_and_create_s3_bucket(bucket_name)

    if return_code == 0:
        print(message)
        print("SUCCESS")
    else:
        print(message)
        print(f"FAILURE: {message}")

    sys.exit(return_code)
