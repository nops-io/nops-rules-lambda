import logging

import boto3
from botocore.exceptions import ClientError


def ebs_delete_volume(resource):
    try:
        volume_id = resource["resource_id"]
        ...
        return f"Volume {volume_id} deleted"

    except ClientError as error:
        logging.error(error)
        print(error)
