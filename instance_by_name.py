import boto3

def get_instance_ids_by_name(instance_names):
    """
    Get a list of EC2 instance IDs that match the provided instance names.

    :param instance_names: List of instance names to search for.
    :return: Dictionary mapping instance names to their corresponding instance IDs.
    """
    ec2 = boto3.client('ec2')

    # Describe instances with the specified name(s)
    response = ec2.describe_instances(
        Filters=[
            {
                'Name': 'tag:Name',
                'Values': instance_names
            }
        ]
    )

    # Create a dictionary to store instance IDs mapped by their names
    instance_ids = {}

    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            for tag in instance['Tags']:
                if tag['Key'] == 'Name' and tag['Value'] in instance_names:
                    instance_name = tag['Value']
                    instance_id = instance['InstanceId']
                    instance_ids[instance_name] = instance_id

    return instance_ids

# Example usage
instance_names = ['instance-1', 'instance-2']
instance_ids = get_instance_ids_by_name(instance_names)
print(instance_ids)
