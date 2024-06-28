# Instructions

Press `Ctrl + Shift + V` or `Cmd + Shift + V` to view this in a nicer way!

This is a summary of how the files work and how you run the latest version of the code. 

## How to run the latest version?

1. Start the lab in AWS Academy

2. Paste all your AWS cretentials into the `config.py` file

        security_group_name     - The name of your secturity group
        key_name                - The name of your key pair (e.g. vockey)
        key_path                - The path to your key (e.g. path/to/vockey.pem)
        region_name             - E.g. us-east-1
        aws_access_key_id       - Found in AWS Academy
        aws_secret_access_key   - Found in AWS Academy
        aws_session_token       - Found in AWS Academy

3. Create the instances by running `create_instances.py`

4. Perform all installations on the instances by running `install_docker.py`. This step might take several minutes to complete. 

5. Run `sudo docker compose ps` on the instances in AWS GUI to see if the installations are complete. 

    Optional: If it takes too long you can do the installation manually instead. Then you have to:
        
        1. Terminate the instances using 'terminate_instance.py' from a new terminal
        2. Restart the instances using 'create_instances.py'
        3. Uncomment line 111 in install_docker.py
        4. Run 'install_docker.py"
        5. Do the following commands manually in the GUI:

            chmod +x install_docker.sh
            ./install_docker.sh
            sudo docker compose build 
            sudo docker compose up -d

6. Find the public IP of the orchestrator in the AWS GUI, this is usually the last instance in the list, by checking if it's the right one, run the command `ls` on the instance in the GUI and see if it has the `container_info.py` file. 

7. Use the public IP of the orchestrator to send a request to it using the `generate_request.py` file

8. Terminate instances using `terminate_instances.py`


