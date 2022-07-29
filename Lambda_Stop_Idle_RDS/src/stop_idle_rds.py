import json
import boto3
from botocore.exceptions import ClientError

client = boto3.client('rds')

def Stop_DB_Instance(DBInstanceIdentifier):
    try:
        response = client.stop_db_instance(
            DBInstanceIdentifier=DBInstanceIdentifier,
        )
        return("Given RDS Instance is Stoped...")
    except ClientError as error:
        if error.response['Error']['Code'] == "InvalidDBInstanceState":
            return("Given RDS Instance is Already Stoped...")
        elif error.response['Error']['Code'] == "DBInstanceNotFound":
            try:
                response = client.stop_db_cluster(
                    DBClusterIdentifier=DBInstanceIdentifier
                )
                return("Given RDS Cluster is Stoped...")
            except ClientError as error:
                if error.response['Error']['Code'] == "DBClusterNotFoundFault":
                    return("Given RDS Cluster is Not Found...")
                elif error.response['Error']['Code'] == "InvalidDBClusterStateFault":
                    return("Given RDS Cluster is Already Stoped...")
                else:    
                    print(error)
            
        else:    
            print(error)

    

def lambda_handler(event, context):
    
    # DBInstanceIdentifier=event['DBInstanceIdentifier']
    DBInstanceIdentifier='database-1'

    return_msg=Stop_DB_Instance(DBInstanceIdentifier)
    

    msg = return_msg
    return {'Message': json.dumps(msg)}