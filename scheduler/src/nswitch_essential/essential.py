import json
import logging

import boto3
from botocore.exceptions import ClientError

from utils import get_ebs_volume_id_from_resource


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


HANDLER_MAP = {
    "ebs": {"ebs_migration": ec2_ebs_migration},
    "asg": {"ebs_migration": asg_ebs_migration},
}


def lambda_handler(event, context):
    action = event["detail"]["action"]
    resources = event["detail"]["scheduler"]["resources"]
    messages = []
    for resource in resources:
        try:
            handler = HANDLER_MAP.get(resource.get("item_type"), {}).get(action)
            messages.append(handler(resource))
        except Exception as e:
            logging.error(e)
            print(e)
    msg = {"results": messages}
    print(msg)
    return {"Message": json.dumps(msg)}
