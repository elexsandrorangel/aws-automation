import boto3


def lambda_handler(event, context):
    ec2 = boto3.client('ec2')

    # List of instance names to stop
    instance_names = ['instance-name-1', 'instance-name-2', 'instance-name-3']

    # Describe instances with the specified names
    instances = ec2.describe_instances(
        Filters=[
            {
                'Name': 'tag:Name',
                'Values': instance_names
            },
            {
                'Name': 'instance-state-name',
                'Values': ['running']  # Only look for running instances
            }
        ]
    )

    # Collect all instance IDs that need to be stopped
    instance_ids = [instance['InstanceId'] for reservation in instances['Reservations'] for instance in reservation['Instances']]

    if instance_ids:
        # Stop the instances
        ec2.stop_instances(InstanceIds=instance_ids)
        print(f'Stopping instances: {instance_ids}')
    else:
        print(f'No running instances found with names: {instance_names}')

    return {
        'statusCode': 200,
        'body': 'Instances stop process initiated.'
    }
