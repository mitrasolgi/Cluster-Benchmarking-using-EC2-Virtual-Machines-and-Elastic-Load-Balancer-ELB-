import paramiko
import boto3
import config
import json
import os
import re

# This code:
# - Connects to the instances using SSH
# - Uploads the files in "Workers" to the worker instances
# - Uploads the files in "Orcehstrator" to the orchestrator instance
# - Executes the install_docker.sh script in the instances

# Returns a list of all running instances
def get_running_instances(ec2_client):
    response = ec2_client.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    instances = []
    for reservation in response['Reservations']:
        instances.extend(reservation['Instances'])
    return instances

# Connects to an instance using SSH
def ssh_connect(instance, private_key_path):
    key = paramiko.RSAKey(filename=private_key_path)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(instance['PublicIpAddress'], username='ubuntu', pkey=key)
    return ssh

# Uploads a file directory to an instance
def upload_directory(ssh, local_path):
    sftp = ssh.open_sftp()
    
    try:
        for root, dirs, files in os.walk(local_path):
            for file in files:
                local_file_path = root + '/' + file
                remote_file_path = file
                sftp.put(local_file_path, remote_file_path)
    
    except Exception as e:
        print(f"Error uploading files from directory {local_path}: {str(e)}")
    finally:
        sftp.close()

def run_docker_installation(ssh):
    command1 = "chmod +x install_docker.sh"
    command2 = "./install_docker.sh &"

    stdin, stdout, stderr = ssh.exec_command(command1)
    print(stdout.read().decode('utf-8'))
    print(stderr.read().decode('utf-8'))
    print("Command 1 done")

    stdin, stdout, stderr = ssh.exec_command(command2)
    print("Command 2 started in the background")

def generate_json_file(worker_ips):
    json_data = {}
    container_count = 1
    worker_ports = [5001, 5002]

    for ip in worker_ips:
        for port in worker_ports:
            container_name = f"container {container_count}"
            json_data[container_name] = {
                "ip": ip,
                "port": str(port),
                "status": "free"
            }
            container_count += 1

    with open('Orchestrator/container_info.json', 'w') as json_file:
        json.dump(json_data, json_file, indent=4)

def update_orchestrator_ip(new_orchestrator_ip):

    file_path = 'config.py'

    # Read the content of the file
    with open(file_path, 'r') as file:
        content = file.read()

    # Update the orchestrator_ip field
    content = re.sub(r'orchestrator_ip\s*=\s*\'[^\']*\'', f'orchestrator_ip = \'{new_orchestrator_ip}\'', content)

    # Write the modified content back to the file
    with open(file_path, 'w') as file:
        file.write(content)

# Installs Docker on all 5 instances and uploads associated directories
def main():
    aws_access_key_id = config.aws_access_key_id
    aws_secret_access_key = config.aws_secret_access_key
    region_name = config.region_name
    aws_session_token=config.aws_session_token
    private_key_path = config.key_path

    # Connects to EC2 client
    ec2_client = boto3.client('ec2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, aws_session_token=aws_session_token, region_name=region_name)

    # Gets all running instances
    instances = get_running_instances(ec2_client)
    worker_ips = []
    
    # Loops through all instances
    for i, instance in enumerate(instances[:5]):
        ssh = None  # Initialize ssh variable outside the try block
        print(f"We are in instance {i}")
        try:
            ssh = ssh_connect(instance, private_key_path)

            # Specifies local directories for each instance
            if i == 4:
                local_directory = 'Orchestrator'
                generate_json_file(worker_ips)
                update_orchestrator_ip(instance['PublicIpAddress'])
            else:
                local_directory = 'Workers'
                worker_ips.append(instance['PublicIpAddress'])

            # Uploads Dockerfile and docker-compose.yml directories
            upload_directory(ssh, local_directory)

            print("Directories uploaded")

            # Run Docker installation script - This line can be commented out if you want to do it manually
            run_docker_installation(ssh)

            print("Docker installed and Flask app running")

        except Exception as e:
            print(f"Error connecting to {instance['InstanceId']}: {str(e)}")
        finally:
            if ssh:
                ssh.close()

if __name__ == "__main__":
    main()
