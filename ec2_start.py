import boto3


def lambda_handler(event, context):
    ec2 = boto3.client('ec2')

    # Replace with the name tag of the instance(s) you want to start
    # instance_name = 'your-instance-name'
    instance_names = ['instance-1', 'instance-2']
    # Describe instances with the specified name
    instances = ec2.describe_instances(
        Filters=[
            {
                'Name': 'tag:Name',
                'Values': instance_names
            },
            {
                'Name': 'instance-state-name',
                'Values': ['stopped']  # Only look for stopped instances
            }
        ]
    )

    # Collect all instance IDs that need to be started
    instance_ids = [instance['InstanceId'] for reservation in instances['Reservations'] for instance in reservation['Instances']]

    if instance_ids:
        # Start the instances
        ec2.start_instances(InstanceIds=instance_ids)
        print(f'Starting instances: {instance_ids}')
    else:
        print(f'No stopped instances found with name: {instance_names}')

    return {
        'statusCode': 200,
        'body': 'Instances start process initiated.'
    }
