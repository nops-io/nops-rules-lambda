#!/bin/bash
ENV="$1"

pip install --target ./package -r src/requirements.txt
cp ./src/main.py ./package
cd package/
zip -r ../main-latest.zip .
cd ..

if [ "$ENV" == "prod" ];then
    aws s3 cp main-latest.zip s3://nops-rules-lambda-sources/scheduler/main-latest.zip --acl public-read
    aws s3 cp scheduler.yml s3://nops-rules-lambda-sources/scheduler/scheduler.yml --acl public-read
    aws s3 cp encrypted_ebs_kms_policy.yml s3://nops-rules-lambda-sources/scheduler/encrypted_ebs_kms_policy.yml --acl public-read
else
    aws s3 cp main-latest.zip s3://nops-rules-lambda-sources/scheduler/main-latest-uat.zip --acl public-read
    aws s3 cp scheduler.yml s3://nops-rules-lambda-sources/scheduler/scheduler-uat.yml --acl public-read
    aws s3 cp encrypted_ebs_kms_policy.yml s3://nops-rules-lambda-sources/scheduler/encrypted_ebs_kms_policy-uat.yml --acl public-read
fi
