import logging

import boto3
from botocore.exceptions import ClientError

from utils import get_bucket_name_from_resource
from utils import get_ebs_volume_id_from_resource
from utils import get_snapshot_id_from_resource


def ec2_ebs_migration(resource):
    try:
        volume_id = get_ebs_volume_id_from_resource(resource)
        ec2_client = boto3.client("ec2", region_name=resource["region"])

        response = ec2_client.describe_volumes(
            VolumeIds=[
                volume_id,
            ],
        )

        volume_type = response["Volumes"][0]["VolumeType"]
        if volume_type != "gp2":
            return f"Volume type is not gp2 - {volume_type}"

        ec2_client.modify_volume(
            VolumeId=volume_id,
            VolumeType="gp3",
        )
        return f"Given EC2 instance is started - {volume_id}"
    except ClientError as error:
        logging.error(error)
        print(error)


def asg_ebs_migration(resource):
    try:
        region = resource["region"]
        ec2_client = boto3.client("ec2", region_name=region)
        asg_client = boto3.client("autoscaling", region_name=region)

        asg_name = resource.get("resource_name", "")
        # get ASG boto3 object by resource name
        asg_obj = asg_client.describe_auto_scaling_groups(
            AutoScalingGroupNames=[asg_name],
        )["AutoScalingGroups"][0]

        launch_template = asg_obj["LaunchTemplate"]
        # if ASG uses launch template
        if launch_template:
            launch_template_id = launch_template["LaunchTemplateId"]
            launch_template_version = launch_template["Version"]

            # get Launch Template Version boto3 object by ID
            launch_template_version_obj = ec2_client.describe_launch_template_versions(
                LaunchTemplateId=launch_template_id,
                Versions=[launch_template_version],
            )["LaunchTemplateVersions"][0]
            launch_template_data = launch_template_version_obj["LaunchTemplateData"]
            block_device_mappings = launch_template_data.get("BlockDeviceMappings", [])

            # change GP2 to GP3 for all block devices
            for block_device_mapping in block_device_mappings:
                if block_device_mapping["Ebs"]["VolumeType"] == "gp2":
                    block_device_mapping["Ebs"]["VolumeType"] = "gp3"

            # create new Launch Template Version based on previous one
            new_launch_template_data = {"BlockDeviceMappings": block_device_mappings}
            new_launch_template_version = ec2_client.create_launch_template_version(
                LaunchTemplateId=launch_template_id,
                SourceVersion=launch_template_version,
                VersionDescription="GP3 volumes",
                LaunchTemplateData=new_launch_template_data,
            )["LaunchTemplateVersion"]
            new_launch_template_version_number = str(new_launch_template_version["VersionNumber"])

            # if the previous Launch Template version was the default one
            if launch_template_version_obj["DefaultVersion"]:  # is True
                # update Launch Template default version
                ec2_client.modify_launch_template(
                    LaunchTemplateId=launch_template_id,
                    DefaultVersion=new_launch_template_version_number,
                )

            if launch_template_version not in ("$Latest", "$Default"):
                # update ASG with new Launch Template version
                asg_client.update_auto_scaling_group(
                    AutoScalingGroupName=asg_obj["AutoScalingGroupName"],
                    LaunchTemplate={
                        "LaunchTemplateId": launch_template_id,
                        "Version": new_launch_template_version_number,
                    },
                )

            # refresh instances in order to apply GP3 volumes immediately
            asg_client.start_instance_refresh(
                AutoScalingGroupName=asg_obj["AutoScalingGroupName"],
                Strategy="Rolling",
            )

            return f"ASG ({asg_name}) volume types are changed."
    except ClientError as error:
        logging.error(error)
        print(error)


def archive_snapshot(resource):
    try:
        # Initialize the EC2 client
        snapshot_id = get_snapshot_id_from_resource(resource)
        ec2_client = boto3.client('ec2', region_name=resource["region"])
        
        # Modify the snapshot attribute to move it to cold storage
        ec2_client.modify_snapshot_tier(
            SnapshotId=snapshot_id,
            StorageTier='archive'
        )
        
        return f"Snapshot {snapshot_id} has been archived."
        
    except ClientError as error:
        logging.error(error)
        print(error)
        return f"Failed to archive snapshot {snapshot_id}."


def s3_intelligent_tiering_migration(resource, configure_archive_tier=False):
    try:
        # Initialize the S3 client
        bucket_name = get_bucket_name_from_resource(resource)
        s3_client = boto3.client('s3')

        # Put the bucket configuration
        s3_client.put_bucket_lifecycle_configuration(
            Bucket=bucket_name,
            LifecycleConfiguration={
                'Rules': [
                    {
                        'ID': f'nOps-Essentials-{bucket_name}-rule',
                        'Filter': {'ObjectSizeGreaterThan': 128},
                        'Status': 'Enabled',
                        'Transitions': [
                            {
                                'Days': 0,
                                'StorageClass': 'INTELLIGENT_TIERING'
                            },
                        ],
                    },
                ],
            },
            ExpectedBucketOwner=resource["account_number"],
        )

        # optional step: configure archive tiers
        if configure_archive_tier:
            configuration_id = f'nOps-Essentials-{bucket_name}-configuration'
            s3_client.put_bucket_intelligent_tiering_configuration(
                Bucket=bucket_name,
                Id=configuration_id,
                IntelligentTieringConfiguration={
                    'Id': configuration_id,
                    'Status': 'Enabled',
                    'Tierings': [
                        {
                            'Days': 90,
                            'AccessTier': 'ARCHIVE_ACCESS',
                        },
                        {
                            'Days': 180,
                            'AccessTier': 'DEEP_ARCHIVE_ACCESS',
                        },
                    ],
                },
            )

        return f"Bucket {bucket_name} has been migrated to Intelligent-Tiering."
    except ClientError as error:
        logging.error(error)
        print(error)
        return f"Failed to migrate bucket {bucket_name} to Intelligent-Tiering."


def s3_intelligent_tiering_migration_with_archiving(resource):
    return s3_intelligent_tiering_migration(resource, configure_archive_tier=True)
