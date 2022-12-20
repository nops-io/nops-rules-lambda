import json
import logging

import boto3
from botocore.exceptions import ClientError


def stop_ec2_instance(resource, action_details=None):
    try:
        instance_id = resource["resource_id"]
        ec2_client = boto3.client("ec2", region_name=resource["region"])
        kwargs = {}
        if action_details and action_details.get("Hibernate"):
            kwargs["Hibernate"] = True
        ec2_client.stop_instances(InstanceIds=[instance_id], **kwargs)
        return f"Given EC2 instance is stopped - {instance_id}"
    except ClientError as error:
        logging.error(error)
        print(error)


def start_ec2_instance(resource, action_details=None):
    try:
        instance_id = resource["resource_id"]
        ec2_client = boto3.client("ec2", region_name=resource["region"])
        ec2_client.start_instances(InstanceIds=[instance_id])
        return f"Given EC2 instance is started - {instance_id}"
    except ClientError as error:
        logging.error(error)
        print(error)


def start_rds_instance(resource, action_details=None):
    try:
        region_name = resource["region"]
        db_identifier = resource["resource_id"].split(":")[-1]
        client = boto3.client("rds", region_name=region_name)
        client.start_db_instance(
            DBInstanceIdentifier=db_identifier,
        )
        return f"Given RDS instance is started  - {db_identifier}"
    except ClientError as error:
        logging.error(error)
        print(error)


def stop_rds_instance(resource, action_details=None):
    try:
        region_name = resource["region"]
        db_identifier = resource["resource_id"].split(":")[-1]
        client = boto3.client("rds", region_name=region_name)
        client.stop_db_instance(
            DBInstanceIdentifier=db_identifier,
        )
        return f"Given RDS instance is stopped - {db_identifier}"
    except ClientError as error:
        logging.error(error)
        print(error)


def update_ec2_auto_scaling(resource, action_details=None):
    try:
        client = boto3.client("autoscaling", region_name=resource["region"])
        autoscaling_id = resource["resource_name"]
        client.update_auto_scaling_group(
            AutoScalingGroupName=autoscaling_id,
            DesiredCapacity=action_details["DesiredCapacity"],
        )
        return f"Given auto scaling group updated- {autoscaling_id}"
    except ClientError as error:
        logging.error(error)
        print(error)


HANDLER_MAP = {
    "ec2": {"start": start_ec2_instance, "stop": stop_ec2_instance},
    "rds": {"start": start_rds_instance, "stop": stop_rds_instance},
    "autoscaling_groups": {"update_ec2_auto_scaling": update_ec2_auto_scaling},
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
    return {"Message": json.dumps(msg)}
