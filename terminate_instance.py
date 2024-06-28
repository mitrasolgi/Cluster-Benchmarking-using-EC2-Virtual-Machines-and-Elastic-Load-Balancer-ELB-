import boto3
import config

# This code terminates all instances automatically
 
# Connect to the EC2 client
ec2 = boto3.client('ec2',
                   aws_access_key_id=config.aws_access_key_id,
                   aws_secret_access_key=config.aws_secret_access_key,
                   aws_session_token=config.aws_session_token,
                   region_name=config.region_name)
 
# Get information about the instances
instance_info = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])

# Extract the instance IDs from the information
instance_ids = []
for reservation in instance_info['Reservations']:
    for instance in reservation['Instances']:
        instance_ids.append(instance['InstanceId'])

# Terminate the 5 instances
ec2.terminate_instances(InstanceIds=instance_ids)

# Wait for the instances to terminate
ec2.get_waiter('instance_terminated').wait(InstanceIds=instance_ids)
print('Instances terminated')

# Delete the security group
security_group = ec2.describe_security_groups(Filters=[{'Name': 'group-name', 'Values': [config.security_group_name]}])
security_group_id = security_group['SecurityGroups'][0]['GroupId']
ec2.delete_security_group(GroupId=security_group_id)
print('Security group terminated')