import json
import logging

import boto3

from utils import get_arn_from_resource
from utils import get_autoscaling_name_from_resource
from utils import get_db_identifier_from_resource
from utils import get_ec2_instance_id_from_resource


# This one would tag resource base on schedule
def update_tag_ec2(resource):
    # create_tags
    instance_id = get_ec2_instance_id_from_resource(resource)
    ec2_client = boto3.client("ec2", region_name=resource["region"])
    tags = resource.get("tags", [])
    # [{"Key": "string", "Value": "string"}]
    ec2_client.create_tags(Resources=[instance_id], Tags=tags)
    return f"Given resource is tagged - EC2: {instance_id}"


def update_tag_rds(resource):
    # add_tags_to_resource
    arn = get_arn_from_resource(resource)
    rds_client = boto3.client("rds", region_name=resource["region"])
    tags = resource.get("tags", [])
    # [{"Key": "string", "Value": "string"}]
    rds_client.add_tags_to_resource(
        ResourceName=arn,
        Tags=tags,
    )
    return f"Given resource is tagged - RDS: {arn}"


def update_tag_rds_cluster(resource):
    # This would update the tag of cluster and get all instance of that cluster and update the tag for them
    db_identifier = get_db_identifier_from_resource(resource)
    arn = get_arn_from_resource(resource)
    tags = resource.get("tags", [])
    # [{"Key": "string", "Value": "string"}]
    rds_client = boto3.client("rds", region_name=resource["region"])
    response = rds_client.add_tags_to_resource(
        ResourceName=arn,
        Tags=tags,
    )

    response = rds_client.describe_db_instances(
        Filters=[{"Name": "db-cluster-id", "Values": [db_identifier]}]
    )

    for db_instance in response["DBInstances"]:
        response = rds_client.add_tags_to_resource(
            ResourceName=db_instance["DBInstanceArn"],
            Tags=tags,
        )
    return f"Given resource is tagged - RDS Cluster {arn}"


def update_tag_autoscaling_group(resource):
    # update autoscaling group
    autoscaling_group_name = get_autoscaling_name_from_resource(resource)
    tags_parameters = []
    tags = resource.get("tags", [])
    # [{"Key": "string", "Value": "string"}]
    as_client = boto3.client("autoscaling", region_name=resource["region"])
    for tag in tags:
        tags_parameters.append(
            {
                "Key": tag["Key"],
                "PropagateAtLaunch": True,
                "ResourceId": autoscaling_group_name,
                "ResourceType": "auto-scaling-group",
                "Value": tag["Value"],
            }
        )
    as_client.create_or_update_tags(Tags=tags_parameters)
    return f"Given resource is tagged - Autoscaling Group {autoscaling_group_name}"


def update_tag_nodegroup(resource):
    # update tag of eks node_group
    client = boto3.client("eks", region_name=resource["region"])
    arn = get_arn_from_resource(resource)
    tags = resource.get("tags", [])
    # [{"Key": "string", "Value": "string"}]
    merged_tags = {d["Key"]: d["Value"] for d in tags}
    client.tag_resource(
        resourceArn=arn,
        tags=merged_tags,
    )
    return f"Given resource is tagged - Nodegroup {arn}"


HANDLER_MAP = {
    "ec2": {"update_tag": update_tag_ec2},
    "rds": {"update_tag": update_tag_rds},
    "rds_cluster": {"update_tag": update_tag_rds_cluster},
    "autoscaling_groups": {"update_tag": update_tag_autoscaling_group},
    "eks_nodegroup": {"update_tag": update_tag_nodegroup},
}


def lambda_handler(event, context):
    action = event["detail"]["action"]
    resources = event["detail"]["resources"]
    messages = []
    for resource in resources:
        try:
            handler = HANDLER_MAP.get(resource.get("item_type"), {}).get(action)
            messages.append(
                handler(
                    resource,
                )
            )
        except Exception as e:
            logging.error(e)
            print(e)
    msg = {"results": messages}
    print(msg)
    return {"Message": json.dumps(msg)}
