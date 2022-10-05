import json
import os

import boto3
from botocore.exceptions import ClientError


def stop_ec2_instance(resources):
    runtime_region = os.environ["AWS_REGION"]
    try:
        ec2_client = boto3.client(
            "ec2", region_name=runtime_region
        )  # Todo get region from resource
        ec2_client.stop_instances(InstanceIds=resources)
        return "Given EC2 instance stopped"
    except ClientError as error:
        print(error)


def start_ec2_instance(resources):
    runtime_region = os.environ["AWS_REGION"]
    try:
        ec2_client = boto3.client(
            "ec2", region_name=runtime_region
        )  # Todo get region from resource
        ec2_client.start_instances(InstanceIds=resources)
        return "Given EC2 instance start"
    except ClientError as error:
        print(error)


def lambda_handler(event, context):

    resources = event["resources"]
    action = event["detail"]["action"]
    if action == "start":
        return_msg = start_ec2_instance(resources)
    if action == "stop":
        return_msg = stop_ec2_instance(resources)

    msg = return_msg
    return {"Message": json.dumps(msg)}
