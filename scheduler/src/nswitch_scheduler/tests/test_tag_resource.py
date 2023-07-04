import json
from unittest.mock import patch

import boto3
from moto import mock_autoscaling
from moto import mock_ec2
from moto import mock_rds
from tag_resource import lambda_handler
from tag_resource import update_tag_autoscaling_group
from tag_resource import update_tag_ec2
from tag_resource import update_tag_nodegroup
from tag_resource import update_tag_rds
from tag_resource import update_tag_rds_cluster

EXAMPLE_AMI_ID = "ami-12c6146b"

LAMBDA_EVENT = {
    "version": "0",
    "id": "6739aa2f-3b23-095d-5ae7-9a7bf8f0b058",
    "detail-type": "nops_scheduler_tag_resource",
    "source": "aws.partner/nops.io/12345677901/nops_uat_notification_12_TrucCF1",
    "account": "12345677901",
    "time": "2022-10-21T07:11:28Z",
    "region": "us-west-2",
    "resources": [
        "arn:aws:rds:us-west-2:12345677901:db:database-running-for-dev-scheduler"
    ],
    "detail": {
        "event_type": "scheduler_tag_resource",
        "action": "update_tag",
        "resources": [
            {
                "resource_id": "arn:aws:rds:us-west-2:123456789012:db:database-running-for-dev-scheduler",
                "resource_name": "database-running-for-dev-scheduler",
                "resource_arn": None,
                "item_type": "rds",
                "tags": [{"Key": "nops-schedule", "Value": "value1,value2"}],
                "region": "us-west-2",
            }
        ],
    },
}


@mock_rds
def test_lambda_handler():
    conn = boto3.client("rds", region_name="us-west-2")
    conn.create_db_instance(
        DBInstanceIdentifier="database-running-for-dev-scheduler",
        AllocatedStorage=10,
        Engine="postgres",
        DBName="staging-postgres",
        DBInstanceClass="db.m1.small",
        LicenseModel="license-included",
        MasterUsername="root",
        MasterUserPassword="hunter2",
        Port=1234,
        DBSecurityGroups=["my_sg"],
        VpcSecurityGroupIds=["sg-123456"],
        EnableCloudwatchLogsExports=["audit", "error"],
    )
    result = lambda_handler(LAMBDA_EVENT, {})
    message = json.loads(result["Message"])
    assert (
        message["results"][0]
        == "Given resource is tagged - RDS: arn:aws:rds:us-west-2:123456789012:db:database-running-for-dev-scheduler"
    )
    tags_result = conn.list_tags_for_resource(
        ResourceName="arn:aws:rds:us-west-2:123456789012:db:database-running-for-dev-scheduler"
    )
    assert tags_result["TagList"] == [
        {"Key": "nops-schedule", "Value": "value1,value2"}
    ]


@mock_ec2
def test_update_tag_ec2():
    ec2 = boto3.resource("ec2", region_name="us-east-1")
    reservation = ec2.create_instances(ImageId=EXAMPLE_AMI_ID, MinCount=2, MaxCount=2)
    instance1, instance2 = reservation
    resource = {
        "resource_id": instance1.id,
        "region": "us-east-1",
        "tags": [{"Key": "nops-schedule", "Value": "value1,value2"}],
    }
    result = update_tag_ec2(resource)
    assert result == f"Given resource is tagged - EC2: {instance1.id}"
    ec2instance = ec2.Instance(instance1.id)
    assert ec2instance.tags == [{"Key": "nops-schedule", "Value": "value1,value2"}]


@mock_rds
def test_update_tag_rds():
    conn = boto3.client("rds", region_name="us-west-2")
    database = conn.create_db_instance(
        DBInstanceIdentifier="db-master-1",
        AllocatedStorage=10,
        Engine="postgres",
        DBName="staging-postgres",
        DBInstanceClass="db.m1.small",
        LicenseModel="license-included",
        MasterUsername="root",
        MasterUserPassword="hunter2",
        Port=1234,
        DBSecurityGroups=["my_sg"],
        VpcSecurityGroupIds=["sg-123456"],
        EnableCloudwatchLogsExports=["audit", "error"],
    )
    db_instance = database["DBInstance"]
    assert db_instance["DBInstanceStatus"] == "available"
    resource = {
        "resource_arn": db_instance["DBInstanceArn"],
        "region": "us-west-2",
        "tags": [{"Key": "nops-schedule", "Value": "value1,value2"}],
    }
    result = update_tag_rds(resource)
    assert (
        result
        == "Given resource is tagged - RDS: arn:aws:rds:us-west-2:123456789012:db:db-master-1"
    )
    tags = conn.list_tags_for_resource(ResourceName=db_instance["DBInstanceArn"])
    assert tags["TagList"] == [{"Key": "nops-schedule", "Value": "value1,value2"}]


@mock_rds
def test_update_tag_rds_cluster():
    conn = boto3.client("rds", region_name="us-west-2")
    conn.create_db_cluster(
        DBClusterIdentifier="db-master-1",
        Engine="aurora-mysql",
        MasterUsername="root",
        MasterUserPassword="hunter1232",
    )

    response = conn.describe_db_clusters(DBClusterIdentifier="db-master-1")
    arn = response["DBClusters"][0]["DBClusterArn"]

    response = conn.create_db_instance(
        DBInstanceIdentifier="db-instance-1",
        DBInstanceClass="db.t2.micro",
        Engine="aurora-mysql",
        DBClusterIdentifier="db-master-1",
        MasterUsername="myuser",
        MasterUserPassword="password",
    )
    resource = {
        "resource_arn": arn,
        "region": "us-west-2",
        "resource_name": "db-master-1",
        "tags": [{"Key": "nops-schedule", "Value": "value1,value2"}],
    }
    result = update_tag_rds_cluster(resource)
    assert (
        result
        == "Given resource is tagged - RDS Cluster arn:aws:rds:us-west-2:123456789012:cluster:db-master-1"
    )
    response = conn.describe_db_clusters(DBClusterIdentifier="db-master-1")
    assert response["DBClusters"][0]["TagList"] == [
        {"Key": "nops-schedule", "Value": "value1,value2"}
    ]
    response = conn.describe_db_instances(DBInstanceIdentifier="db-instance-1")
    assert response["DBInstances"][0]["TagList"] == [
        {
            "Key": "nops-schedule",
            "Value": "value1,value2",
        }
    ]


@mock_autoscaling
def test_update_tag_autoscaling_group():
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
        Tags=[],
    )
    details = conn.describe_auto_scaling_groups(AutoScalingGroupNames=["TestGroup1"])
    resource = {
        "resource_arn": details["AutoScalingGroups"][0]["AutoScalingGroupARN"],
        "region": "us-east-1",
        "resource_name": "TestGroup1",
        "tags": [{"Key": "nops-schedule", "Value": "value1,value2"}],
    }
    result = update_tag_autoscaling_group(resource)
    assert result == "Given resource is tagged - Autoscaling Group TestGroup1"
    details = conn.describe_auto_scaling_groups(AutoScalingGroupNames=["TestGroup1"])
    assert details["AutoScalingGroups"][0]["Tags"][0] == {
        "ResourceId": "TestGroup1",
        "ResourceType": "auto-scaling-group",
        "Key": "nops-schedule",
        "Value": "value1,value2",
        "PropagateAtLaunch": True,
    }


def test_update_tag_nodegroup():

    node_arn = (
        "arn:aws:eks:us-east-1:123456789012:nodegroup/test-cluster/test-node-group/"
    )
    resource = {
        "id": 535,
        "created": "2022-12-05T19:17:25.311392Z",
        "modified": "2022-12-05T19:17:25.311392Z",
        "item_type": "eks_nodegroup",
        "item_id": "1234556",
        "resource_id": node_arn,
        "resource_arn": node_arn,
        "tags": [{"Key": "nops-schedule", "Value": "value1,value2"}],
        "region": "us-east-1",
    }
    with patch("boto3.client") as mock_client:
        mock_eks = mock_client.return_value
        mock_eks.tag_resource.return_value = {}
        result = update_tag_nodegroup(resource)
        mock_eks.tag_resource.assert_called_once_with(
            resourceArn=node_arn, tags={"nops-schedule": "value1,value2"}
        )
    assert (
        result
        == "Given resource is tagged - Nodegroup arn:aws:eks:us-east-1:123456789012:nodegroup/test-cluster/test-node-group/"
    )
