import boto3
from main import lambda_handler
from main import start_autoscaling_group
from main import stop_autoscaling_group
from moto import mock_autoscaling
from moto import mock_eks

from .conftest import AUTOSCALING_EVENT

EXAMPLE_AMI_ID = "ami-12c6146b"


@mock_eks
@mock_autoscaling
def test_autoscaling_start():
    conn = boto3.client("autoscaling", region_name="us-east-1")

    conn.create_launch_configuration(
        LaunchConfigurationName="TestLC",
        ImageId=EXAMPLE_AMI_ID,
        InstanceType="t2.medium",
    )

    conn.create_auto_scaling_group(
        AutoScalingGroupName="TestGroup1",
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
    resource = {
        "resource_id": "TestGroup1",
        "region": "us-east-1",
        "resource_name": "TestGroup1",
    }
    action_details = {}
    stop_autoscaling_group(resource, action_details)
    details = conn.describe_auto_scaling_groups(AutoScalingGroupNames=["TestGroup1"])
    assert details["AutoScalingGroups"][0]["DesiredCapacity"] == 0


@mock_eks
@mock_autoscaling
def test_autoscaling_stop():
    conn = boto3.client("autoscaling", region_name="us-east-1")

    conn.create_launch_configuration(
        LaunchConfigurationName="TestLC",
        ImageId=EXAMPLE_AMI_ID,
        InstanceType="t2.medium",
    )

    conn.create_auto_scaling_group(
        AutoScalingGroupName="TestGroup1",
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
    resource = {
        "resource_id": "TestGroup1",
        "region": "us-east-1",
        "resource_name": "TestGroup1",
        "resource_details": {"MinSize": 1, "MaxSize": 1, "DesiredCapacity": 1},
    }
    action_details = {}
    start_autoscaling_group(resource, action_details)
    details = conn.describe_auto_scaling_groups(AutoScalingGroupNames=["TestGroup1"])
    assert details["AutoScalingGroups"][0]["DesiredCapacity"] == 1
