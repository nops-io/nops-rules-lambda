import logging

import boto3
from botocore.exceptions import ClientError


def ec2_rightsizing(resource):
    try:
        region = resource["region"]
        instance_id = resource["resource_id"]
        new_instance_type = resource["resource_details"]["recommended_instance_type"]

        # Initialize the EC2 client
        ec2 = boto3.client("ec2", region_name=region)

        # Stop the EC2 instance
        ec2.stop_instances(InstanceIds=[instance_id])

        # Wait for the instance to stop
        waiter = ec2.get_waiter("instance_stopped")
        waiter.wait(InstanceIds=[instance_id])

        # Modify the instance type
        ec2.modify_instance_attribute(
            InstanceId=instance_id,
            InstanceType={"Value": new_instance_type}
        )

        # Start the EC2 instance
        ec2.start_instances(InstanceIds=[instance_id])

        return f"Instance {instance_id} resized to {new_instance_type}"

    except ClientError as error:
        logging.error(error)
        print(error)
