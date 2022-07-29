import boto3
from botocore.exceptions import ClientError
import datetime
import json
import os
import logging
import sys

FinalData = []
Excluded_Users_Text = "<html><body><h3>Following are the users that are Excluded form the list :<h3></body></html>"
Excluded_Users_HeadingRow = "<body><table style=width:50%><tr><th style='border:1px solid black;'>UserName</th>"

Keys_Age_Users_Text = "<body><h3>Following are the age of the Keys:<h3></body></html>"
Keys_Age_HeadingRow = "<body><table style=width:70%><tr><th style='border:1px solid black;'>UserName</th><th style='border:1px solid black;'>Key</th><th style='border:1px solid black;'>KeyAge</th></tr>"

Password_Age_Users_Text = "<body><h3>Following are the age of the Password:<h3></body></html>"
Password_Age_HeadingRow = "<body><table style=width:150%><tr><th style='border:1px solid black;'>UserName</th><th style='border:1px solid black;'>PasswordAge</th></tr>"


EndRow = "</table></body></html>"

iam_client = boto3.client('iam')

def email_function(EmailString,aws_account_id):
    SENDER = os.environ['Sender_Email']
    CONFIGURATION_SET = "ConfigSet"
    AWS_REGION = "us-east-1"
    SUBJECT = "Report of AWS IAM User KeyRotation and IAM Audit for Account: "+aws_account_id
    BODY_TEXT = ("Amazon SES Test (Python)\r\n"
             "This email was sent with Amazon SES using the "
             "AWS SDK for Python (Boto)."
            )
    BODY_HTML = EmailString      
    CHARSET = "UTF-8"
    RECIPIENTS = os.environ['Recipient_Email'].split(',')
    client = boto3.client('ses',region_name=AWS_REGION)
    try:
        response = client.send_email(
            Destination={
                'ToAddresses': RECIPIENTS
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
    

def list_user(user):
    userdetails=iam_client.list_access_keys(UserName=user)
    days = []
    singlekey = []
    if len(userdetails['AccessKeyMetadata']) >0 :
        for keys in userdetails['AccessKeyMetadata']:
            singlekey.append(keys['AccessKeyId'])
            CreationDate = keys['CreateDate']
            days.append(time_diff(CreationDate))
    else:
        days.append(0)
    return (days,singlekey)

        
def users_password(user):
    try:
        password_details = iam_client.get_login_profile(UserName=user)
        CreationDate = password_details['LoginProfile']['CreateDate']
        PasswordDays = time_diff(password_details['LoginProfile']['CreateDate'])
        return PasswordDays
    except ClientError as e:
        if e.response['Error']['Code'] == "NoSuchEntity":
            PasswordDays = 0
            return PasswordDays 

        

def time_diff(keycreatedtime):
    now=datetime.datetime.now(datetime.timezone.utc)
    diff=now-keycreatedtime
    return diff.days


def log_exception(e):
    print(str(e))
    logging.error("Exception: {}".format(e), exc_info=sys.exc_info())

def lambda_handler(event, context):
    try:
        aws_account_id = context.invoked_function_arn.split(":")[4]
        Excluded_Users = ""
        Keys_Age = ""
        Password_Age = ""
        response=[]
        Asterisk="***************"
        details = iam_client.list_users(MaxItems=300)
        for user_name in details['Users']:
            user = user_name['UserName']
            if user in os.environ['Excluded_Users']:
                TempExcluded_Users = "<tr><td style='border:1px solid black; width:80% '>"+user+"</td></tr>"
                Excluded_Users = Excluded_Users + TempExcluded_Users
            else:
                KeyDays = list_user(user)
                SingleKeyDays = KeyDays[0]
                AccessKeyId = KeyDays[1]
                for Days,Key in zip(SingleKeyDays,AccessKeyId):
                    Key=Key[15:20]
                    if Days > int(os.environ['Rotate_Key_Days']):
                        TempKeyAge = "<tr><td style='border:1px solid black; text-align:center;'>"+user+"</td><td style='border:1px solid black; text-align:center;background-color:red;'>"+Asterisk+Key+"</td><td style='border:1px solid black;text-align:center;background-color:red;'>"+str(Days)+" Days""</tr>"
                    elif Days > int(os.environ['Alert_Key_Days']):
                        TempKeyAge = "<tr><td style='border:1px solid black; text-align:center;'>"+user+"</td><td style='border:1px solid black; text-align:center;background-color:orange;'>"+Asterisk+Key+"</td><td style='border:1px solid black;text-align:center;background-color:orange;'>"+str(Days)+" Days""</tr>"
                    else:
                        TempKeyAge = "<tr><td style='border:1px solid black;text-align:center;'>"+user+"</td><td style='border:1px solid black; text-align:center;'>"+Asterisk+Key+"</td><td style='border:1px solid black;text-align:center;'>"+str(Days)+" Days""</tr>"
                    Keys_Age = Keys_Age + TempKeyAge
                
                PasswordDays = users_password(user)
                if PasswordDays > int(os.environ['Rotate_Password_Days']):
                    TempPasswordAge = "<tr><td style='border:1px solid black; text-align:center;'>"+user+"</td><td style='border:1px solid black;text-align:center;background-color:red;'>"+str(PasswordDays)+" Days""</tr>"
                elif PasswordDays > int(os.environ['Alert_Password_Days']):
                    TempPasswordAge = "<tr><td style='border:1px solid black; text-align:center;'>"+user+"</td><td style='border:1px solid black;text-align:center;background-color:orange;'>"+str(PasswordDays)+" Days""</tr>"
                else:
                    TempPasswordAge = "<tr><td style='border:1px solid black;text-align:center;'>"+user+"</td><td style='border:1px solid black;text-align:center;'>"+str(PasswordDays)+" Days""</tr>"
                Password_Age = Password_Age + TempPasswordAge
                
    
        EmailString = ""  
        if Excluded_Users:
            FinalData.append(str(Excluded_Users_Text))
            FinalData.append(str(Excluded_Users_HeadingRow))
            FinalData.append(str(Excluded_Users))
      
        if Keys_Age:
            FinalData.append(str(Keys_Age_Users_Text))
            FinalData.append(str(Keys_Age_HeadingRow))
            FinalData.append(str(Keys_Age))
    
        if Password_Age:
            FinalData.append(str(Password_Age_Users_Text))
            FinalData.append(str(Password_Age_HeadingRow))
            FinalData.append(str(Password_Age))    
       
        
        FinalData.append(str(EndRow))
        EmailString = EmailString.join(FinalData)
        email_function(EmailString=EmailString, aws_account_id=aws_account_id)
        msg = "Successfull execution."
        return {'statusCode': 200,'Message': json.dumps(msg)}
        
        
    except Exception as e:
        StatusCode = 500                                                                                    
        log_exception(e)
        msg = "Process has encountered an internal server error."
    return {'statusCode': StatusCode,'Message': json.dumps(msg)}