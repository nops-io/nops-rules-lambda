import json

import boto3
from main import lambda_handler
from moto import mock_autoscaling
from moto import mock_eks

from .conftest import NODEGROUP_START_LAMBDA_EVENT

EXAMPLE_AMI_ID = "ami-12c6146b"


@mock_eks
@mock_autoscaling
def test_handle_nodegroup_start_stop():
    conn = boto3.client("eks", region_name="us-east-1")

    conn.create_cluster(
        name="test-cluster",
        roleArn="arn:aws:iam::123456789012:role/test_role",
        resourcesVpcConfig={
            "securityGroupIds": [
                "sg-6979fe18",
            ],
            "subnetIds": [
                "subnet-6782e71e",
                "subnet-e7e761ac",
            ],
        },
    )
    node_group = conn.create_nodegroup(
        clusterName="test-cluster",
        nodegroupName="test-node-group",
        nodeRole="arn:aws:iam::123456789012:role/test_role_node",
        subnets=["subnet-6782e71e", "subnet-e7e761ac"],
        scalingConfig={"minSize": 3, "maxSize": 3, "desiredSize": 3},
    )
    conn = boto3.client("autoscaling", region_name="us-east-1")

    conn.create_launch_configuration(
        LaunchConfigurationName="TestLC",
        ImageId=EXAMPLE_AMI_ID,
        InstanceType="t2.medium",
    )
    autoscaling_group_name = node_group["nodegroup"]["resources"]["autoScalingGroups"][
        0
    ]["name"]

    conn.create_auto_scaling_group(
        AutoScalingGroupName=autoscaling_group_name,
        MinSize=1,
        DesiredCapacity=6,
        MaxSize=10,
        LaunchConfigurationName="TestLC",
        AvailabilityZones=["us-east-1e"],
        Tags=[
            {
                "ResourceId": "arn:TestGroup1",
                "ResourceType": "auto-scaling-group",
                "PropagateAtLaunch": True,
                "Key": "TestTagKey1",
                "Value": "TestTagValue1",
            }
        ],
    )

    node_arn = node_group["nodegroup"]["nodegroupArn"]
    resource = {
        "id": 535,
        "created": "2022-12-05T19:17:25.311392Z",
        "modified": "2022-12-05T19:17:25.311392Z",
        "item_type": "eks_nodegroup",
        "item_id": "1234556",
        "resource_id": node_arn,
        "resource_name": "test-node-group",
        "resource_arn": None,
        "state": "active",
        "region": "us-east-1",
        "scheduler": "db140d55-bb88-4283-b24f-5fbb8e528598",
    }
    NODEGROUP_START_LAMBDA_EVENT["detail"]["scheduler"]["resources"] = [resource]

    result = lambda_handler(NODEGROUP_START_LAMBDA_EVENT, {})
    message = json.loads(result["Message"])
    assert message["results"][0].startswith(
        "Given EKS NodeGroup is started - arn:aws:eks:us-east-1:123456789012:nodegroup/test-cluster/test-node-group/"
    )
    assert "Given auto scaling group updated" in message["results"][0]
    details = conn.describe_auto_scaling_groups(
        AutoScalingGroupNames=[autoscaling_group_name]
    )
    assert details["AutoScalingGroups"][0]["DesiredCapacity"] == 3
    assert details["AutoScalingGroups"][0]["MaxSize"] == 5
    assert details["AutoScalingGroups"][0]["MinSize"] == 1

    NODEGROUP_START_LAMBDA_EVENT["detail"]["action"] = "stop"
    result = lambda_handler(NODEGROUP_START_LAMBDA_EVENT, {})
    message = json.loads(result["Message"])
    assert message["results"][0].startswith(
        "Given EKS NodeGroup is stopped - arn:aws:eks:us-east-1:123456789012:nodegroup/test-cluster/test-node-group/"
    )
    assert "Given auto scaling group updated" in message["results"][0]
    details = conn.describe_auto_scaling_groups(
        AutoScalingGroupNames=[autoscaling_group_name]
    )
    assert details["AutoScalingGroups"][0]["DesiredCapacity"] == 0
    assert details["AutoScalingGroups"][0]["MaxSize"] == 0
    assert details["AutoScalingGroups"][0]["MinSize"] == 0
