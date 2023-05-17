import json
import logging

import boto3
from botocore.exceptions import ClientError

from utils import get_arn_from_resource
from utils import get_autoscaling_name_from_resource
from utils import get_db_identifier_from_resource
from utils import get_ec2_instance_id_from_resource


def stop_ec2_instance(resource, action_details=None):
    try:
        instance_id = get_ec2_instance_id_from_resource(resource)
        ec2_client = boto3.client("ec2", region_name=resource["region"])
        kwargs = {}
        is_hibernate = False
        if action_details and action_details.get("Hibernate"):
            kwargs["Hibernate"] = True
            is_hibernate = True
        try:
            ec2_client.stop_instances(InstanceIds=[instance_id], **kwargs)
        except ClientError as e:
            if "UnsupportedHibernationConfiguration" in str(e) and is_hibernate:
                ec2_client.stop_instances(InstanceIds=[instance_id])
            else:
                raise e
        return f"Given EC2 instance is stopped - {instance_id}"
    except ClientError as error:
        logging.error(error)
        print(error)


def start_ec2_instance(resource, action_details=None):
    try:
        instance_id = get_ec2_instance_id_from_resource(resource)
        ec2_client = boto3.client("ec2", region_name=resource["region"])
        ec2_client.start_instances(InstanceIds=[instance_id])
        return f"Given EC2 instance is started - {instance_id}"
    except ClientError as error:
        logging.error(error)
        print(error)


def start_rds_instance(resource, action_details=None):
    try:
        db_identifier = get_db_identifier_from_resource(resource)
        region_name = resource["region"]
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
        db_identifier = get_db_identifier_from_resource(resource)
        client = boto3.client("rds", region_name=region_name)
        client.stop_db_instance(
            DBInstanceIdentifier=db_identifier,
        )
        return f"Given RDS instance is stopped - {db_identifier}"
    except ClientError as error:
        logging.error(error)
        print(error)


def start_rds_cluster(resource, action_details=None):
    try:
        region_name = resource["region"]
        db_identifier = get_db_identifier_from_resource(resource)
        client = boto3.client("rds", region_name=region_name)
        client.start_db_cluster(
            DBClusterIdentifier=db_identifier,
        )
        return f"Given RDS cluster is started  - {db_identifier}"
    except ClientError as error:
        logging.error(error)
        print(error)


def stop_rds_cluster(resource, action_details=None):
    try:
        region_name = resource["region"]
        db_identifier = get_db_identifier_from_resource(resource)
        client = boto3.client("rds", region_name=region_name)
        client.stop_db_cluster(
            DBClusterIdentifier=db_identifier,
        )
        return f"Given RDS cluster is stopped - {db_identifier}"
    except ClientError as error:
        logging.error(error)
        print(error)


def update_ec2_auto_scaling(resource, action_details=None):
    try:
        client = boto3.client("autoscaling", region_name=resource["region"])
        autoscaling_id = get_autoscaling_name_from_resource(resource)
        kwargs = {}
        if "DesiredCapacity" in action_details:
            kwargs["DesiredCapacity"] = action_details["DesiredCapacity"]
        if "MinSize" in action_details:
            kwargs["MinSize"] = action_details["MinSize"]
        if "MaxSize" in action_details:
            kwargs["MaxSize"] = action_details["MaxSize"]

        client.update_auto_scaling_group(AutoScalingGroupName=autoscaling_id, **kwargs)
        return f"Given auto scaling group updated - {autoscaling_id}"
    except ClientError as error:
        logging.error(error)
        print(error)


def update_nodegroup_scaling(resource, action):
    try:
        region_name = resource["region"]
        node_group_arn = get_arn_from_resource(resource)
        resource_details = resource["resource_details"]
        clusterName = node_group_arn.split("/")[1]
        nodegroupName = node_group_arn.split("/")[2]
        client = boto3.client("eks", region_name=region_name)

        if action == "start":
            scalingConfig = resource_details.get("scalingConfig", {})
            as_action_details = {
                "MinSize": scalingConfig.get("minSize"),
                "DesiredCapacity": scalingConfig.get("desiredSize"),
                "MaxSize": scalingConfig.get("maxSize"),
            }
        elif action == "stop":
            as_action_details = {
                "MinSize": 0,
                "DesiredCapacity": 0,
                "MaxSize": 0,
            }
        else:
            logging.error("Missing action")
            return

        autoscaling_groups = client.describe_nodegroup(
            clusterName=clusterName, nodegroupName=nodegroupName
        )["nodegroup"]["resources"]["autoScalingGroups"]
        autoscaling_group_names = [
            autoscaling_group["name"] for autoscaling_group in autoscaling_groups
        ]
        results = ""
        for autoscaling_group_name in autoscaling_group_names:
            resource = {"resource_name": autoscaling_group_name, "region": region_name}
            result = update_ec2_auto_scaling(resource, action_details=as_action_details)
            if result:
                results += " " + result
        return results
    except ClientError as error:
        logging.error(error)
        print(error)


def start_nodegroup(resource, action_details=None):
    try:
        node_group_arn = get_arn_from_resource(resource)
        results = update_nodegroup_scaling(resource=resource, action="start")
        if results:
            return f"Given EKS NodeGroup is started - {node_group_arn}" + results
        else:
            return f"Given EKS NodeGroup has problem when starting - {node_group_arn}"
    except ClientError as error:
        logging.error(error)
        print(error)


def stop_nodegroup(resource, action_details=None):
    try:
        node_group_arn = get_arn_from_resource(resource)
        results = update_nodegroup_scaling(resource=resource, action="stop")
        if results:
            return f"Given EKS NodeGroup is stopped - {node_group_arn}" + results
        else:
            return f"Given EKS NodeGroup has problem when stopping - {node_group_arn}"
    except ClientError as error:
        logging.error(error)
        print(error)


def start_autoscaling_group(resource, action_details=None):
    try:
        autoscaling_group_arn = get_arn_from_resource(resource)
        resource_details = resource["resource_details"]
        action_details = {
            "MinSize": resource_details.get("MinSize"),
            "DesiredCapacity": resource_details.get("DesiredCapacity"),
            "MaxSize": resource_details.get("MaxSize"),
        }
        results = update_ec2_auto_scaling(
            resource=resource, action_details=action_details
        )
        if results:
            return (
                f"Given autoscaling group is started - {autoscaling_group_arn}"
                + results
            )
        else:
            return f"Given eks nodegroup has problem when starting - {autoscaling_group_arn}"
    except ClientError as error:
        logging.error(error)
        print(error)


def stop_autoscaling_group(resource, action_details=None):
    try:
        autoscaling_group_arn = get_arn_from_resource(resource)
        action_details = {"MinSize": 0, "DesiredCapacity": 0, "MaxSize": 0}
        results = update_ec2_auto_scaling(
            resource=resource, action_details=action_details
        )
        if results:
            return f"Given eks nodegroup is started - {autoscaling_group_arn}" + results
        else:
            return f"Given eks nodegroup has problem when starting - {autoscaling_group_arn}"
    except ClientError as error:
        logging.error(error)
        print(error)


def modify_db_instance(resource, action_details=None):
    try:
        region_name = resource["region"]
        db_identifier = get_db_identifier_from_resource(resource)
        kwargs = {}
        if action_details:
            if action_details.get("DBInstanceClass"):
                kwargs["DBInstanceClass"] = action_details.get("DBInstanceClass")
            if action_details.get("ApplyImmediately"):
                kwargs["ApplyImmediately"] = action_details.get("ApplyImmediately")
        client = boto3.client("rds", region_name=region_name)
        client.modify_db_instance(DBInstanceIdentifier=db_identifier, **kwargs)
        return f"Given RDS instance is modified - {db_identifier}"
    except ClientError as error:
        logging.error(error)
        print(error)


HANDLER_MAP = {
    "ec2": {"start": start_ec2_instance, "stop": stop_ec2_instance},
    "rds": {
        "start": start_rds_instance,
        "stop": stop_rds_instance,
        "modify": modify_db_instance,
    },
    "rds_cluster": {
        "start": start_rds_cluster,
        "stop": stop_rds_cluster,
    },
    "autoscaling_groups": {
        "update_ec2_auto_scaling": update_ec2_auto_scaling,
        "start": start_autoscaling_group,
        "stop": stop_autoscaling_group,
    },
    "eks_nodegroup": {
        "start": start_nodegroup,
        "stop": stop_nodegroup,
    },
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
