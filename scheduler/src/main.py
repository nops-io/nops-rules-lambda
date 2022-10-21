import json

import boto3
from botocore.exceptions import ClientError


def stop_ec2_instance(resource):
    try:
        instance_id = resource["resource_id"]
        ec2_client = boto3.client(
            "ec2", region_name=resource["region"]
        )  # Todo get region from resource
        ec2_client.stop_instances(InstanceIds=[instance_id])
        return f"Given EC2 instance is stopped - {instance_id}"
    except ClientError as error:
        print(error)


def start_ec2_instance(resource):
    try:
        instance_id = resource["resource_id"]
        ec2_client = boto3.client(
            "ec2", region_name=resource["region"]
        )  # Todo get region from resource
        response = ec2_client.start_instances(InstanceIds=[instance_id])
        return f"Given EC2 instance is started - {instance_id}"
    except ClientError as error:
        print(error)


def start_rds_instance(resource):
    try:
        region_name = resource["region"]
        db_identifier = resource["resource_id"].split(":")[-1]
        client = boto3.client("rds", region_name=region_name)
        client.start_db_instance(
            DBInstanceIdentifier=db_identifier,
        )
        return f"Given RDS instance is started  - {db_identifier}"
    except ClientError as error:
        from pprint import pprint;import pdb; pdb.set_trace()  # fmt: skip
        print(error)


def stop_rds_instance(resource):
    try:
        region_name = resource["region"]
        db_identifier = resource["resource_id"].split(":")[-1]
        client = boto3.client("rds", region_name=region_name)
        client.stop_db_instance(
            DBInstanceIdentifier=db_identifier,
        )
        return f"Given RDS instance is stopped - {db_identifier}"
    except ClientError as error:
        print(error)


HANDLER_MAP = {
    "ec2": {"start": start_ec2_instance, "stop": stop_ec2_instance},
    "rds": {"start": start_rds_instance, "stop": stop_rds_instance},
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
            print(e)
    msg = {"results": messages}
    return {"Message": json.dumps(msg)}
