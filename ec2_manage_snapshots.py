import boto3
import datetime


def lambda_handler(event, context):
    main()


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
                    instance_id = instance['InstanceId']
                    instance_name = tag['Value']
                    instance_ids[instance_name] = instance_id
                    # instance_ids.append(instance_id)
    print(instance_ids)
    return instance_ids


def main():
    ec2 = boto3.client('ec2')

    # List of instance IDs for which you want to create snapshots
    instance_names = ['instance-1', 'instance-2']
    instances = get_instance_ids_by_name(instance_names)

    instance_id = ''

    # Iterate over each instance to create snapshots for its volumes
    for instance_name in instances:
        try:
            # Describe the instance to get volume IDs
            instance_id = instances[instance_name]
            response = ec2.describe_instances(InstanceIds=[instance_id])
            for reservation in response['Reservations']:
                 for instance in reservation['Instances']:
                     for volume in instance['BlockDeviceMappings']:
                         volume_id = volume['Ebs']['VolumeId']

                         # Create a snapshot for the volume
                         snapshot = ec2.create_snapshot(
                             VolumeId=volume_id,
                             Description=f'Snapshot of {volume_id} from instance {instance_id}'
                         )

                         # Tag the snapshot (optional, customize tags as needed)
                         ec2.create_tags(
                             Resources=[snapshot['SnapshotId']],
                             Tags=[
                                 {'Key': 'Name', 'Value': f'{instance_name}_{instance_id}'},
                                 {'Key': 'CreatedBy', 'Value': 'Lambda'},
                                 {'Key': 'Cleanup', 'Value': 'true'},
                                 {'Key': 'VolumeId', 'Value': f'{volume_id}'},
                             ]
                         )
                         print(
                             f"Created snapshot {snapshot['SnapshotId']} for volume {volume_id} from instance {instance_id}")
        except Exception as e:
            print(f"Error creating snapshot for instance {instance_name} ({instance_id}): {e}")

    # Define the cutoff date for old snapshots (4 months ago)
    cutoff_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=4 * 30)

    # Delete snapshots older than 4 months for the specified instances
    for instance_name in instances:
         try:
             # Describe snapshots created by the Lambda function
             response = ec2.describe_snapshots(
                 Filters=[
                     {'Name': 'tag:CreatedBy', 'Values': ['Lambda']},
                     {'Name': 'tag:Name', 'Values': [f'{instance_name}_{instance_id}']},
                     {'Name': 'tag:Cleanup', 'Values': ['true']},
                 ]
             )

             for snapshot in response['Snapshots']:
                 start_time = snapshot['StartTime']
                 if start_time < cutoff_date:
                     snapshot_id = snapshot['SnapshotId']
                     ec2.delete_snapshot(SnapshotId=snapshot_id)
                     print(f"Deleted snapshot {snapshot_id} created on {start_time} for instance {instance_id}")
         except Exception as e:
             print(f"Error deleting old snapshots for instance {instance_id}: {e}")

    return {
        'statusCode': 200,
        'body': 'Snapshots created and old snapshots deleted successfully.'
    }


if __name__ == '__main__':
    main()
