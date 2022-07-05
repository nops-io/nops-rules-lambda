import json
import boto3
from botocore.exceptions import ClientError

client = boto3.client('ec2')

def Verify_Volume(volume_id):
    try:
        response = client.describe_volumes(
            VolumeIds=[
                volume_id,
            ]
        )
    except ClientError as error:
        if error.response['Error']['Code'] == "InvalidParameterValue":
            print("Given EBS Volume is Invalid!!!")
            
def Delete_Volume(volume_id):
    try:
        response = client.delete_volume(
            VolumeId=volume_id,
        )
        return("Given EBS Volume is Deleted...")
    except ClientError as error:
        if error.response['Error']['Code'] == "VolumeInUse":
            return("Given EBS Volume is in Use!!!")   

def lambda_handler(event, context):
    
    # volume_id=event.volume_id
    volume_id="vol-091af7ea55470d6d7"
    Verify_Volume(volume_id)
    
    return_msg=Delete_Volume(volume_id)
    
    msg = return_msg
    return {'Message': json.dumps(msg)}
