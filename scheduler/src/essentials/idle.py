import logging

import boto3
from botocore.exceptions import ClientError

from utils import get_ebs_volume_id_from_resource
from utils import get_ec2_instance_id_from_resource


def terminate_ec2_instance(resource):
    # Terminate the instance
    try:
        instance_id = get_ec2_instance_id_from_resource(resource)
        ec2_client = boto3.client("ec2", region_name=resource["region"])
        # ec2_client.terminate_instances(InstanceIds=[instance_id])
        return f"Given EC2 instance is Terminated - {instance_id}"
    except ClientError as error:
        logging.error(error)
        print(error)


def ebs_cleanup_with_snapshot(resource):
    try:
        # Get the volume Id and EC2 client
        volume_id = get_ebs_volume_id_from_resource(resource)
        ec2_client = boto3.client("ec2", region_name=resource["region"])

        # Get tags from the volume + Update tag keys with the prefix "ebs_tag_" + add custom nops tags
        response = ec2_client.describe_volumes(VolumeIds=[volume_id])
        original_tags = response['Volumes'][0].get('Tags', [])

        new_tags = [{'Key': f'ebs_tag_{tag["Key"]}', 'Value': tag["Value"]} for tag in original_tags]
        new_tags.append({'Key': 'nops_essentials', 'Value': 'ebs_cleanup_snapshot'})
        new_tags.append({'Key': 'nops_essentials_cleanup_vol_id', 'Value': volume_id})

        # Create a snapshot of the given EBS volume with all tags included
        snapshot = ec2_client.create_snapshot(VolumeId=volume_id, TagSpecifications=[
            {
                'ResourceType': 'snapshot',
                'Tags': new_tags
            }
        ])

        # Delete the EBS volume
        ec2_client.delete_volume(VolumeId=volume_id)

        return f'Snapshot {snapshot["SnapshotId"]} created and volume {volume_id} deleted'

    except ClientError as error:
        logging.error(error)
        print(error)


def ebs_cleanup_without_snapshot(resource):
    try:
        # Get the volume Id and EC2 client
        volume_id = get_ebs_volume_id_from_resource(resource)
        ec2_client = boto3.client("ec2", region_name=resource["region"])

        # Delete the EBS volume
        ec2_client.delete_volume(VolumeId=volume_id)

        return f'AWS EBS Volume {volume_id} deleted'

    except ClientError as error:
        logging.error(error)
        print(error)
