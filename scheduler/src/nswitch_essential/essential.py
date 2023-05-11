import json
import logging

import boto3
from botocore.exceptions import ClientError

from utils import get_ebs_volume_id_from_resource


def ebs_migration(resource, action_details=None):
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


HANDLER_MAP = {
    "ebs": {"ebs_migration": ebs_migration},
}


def lambda_handler(event, context):
    action = event["detail"]["action"]
    resources = event["detail"]["scheduler"]["resources"]
    action_details = event["detail"].get("action_details")
    messages = []
    for resource in resources:
        try:
            handler = HANDLER_MAP.get(resource.get("item_type"), {}).get(action)
            messages.append(
                handler(
                    resource,
                    action_details=action_details,
                )
            )
        except Exception as e:
            logging.error(e)
            print(e)
    msg = {"results": messages}
    print(msg)
    return {"Message": json.dumps(msg)}
