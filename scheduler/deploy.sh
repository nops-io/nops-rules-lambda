#!/bin/bash
ENV="$1"

pip install --target ./package -r src/nswitch_scheduler/requirements.txt
cp ./src/nswitch_scheduler/*.py ./package
cd package/
zip -r ../main-latest.zip .
cd ..

if [ "$ENV" == "prod" ];then
    aws s3 cp main-latest.zip s3://nops-rules-lambda-sources/scheduler/main-latest.zip --acl public-read
    aws s3 cp cloudformation_templates/scheduler.yml s3://nops-rules-lambda-sources/scheduler/scheduler.yml --acl public-read
    aws s3 cp cloudformation_templates/encrypted_ebs_kms_policy.yml s3://nops-rules-lambda-sources/scheduler/encrypted_ebs_kms_policy.yml --acl public-read
else
    aws s3 cp main-latest.zip s3://nops-rules-lambda-sources/scheduler/main-latest-uat.zip --acl public-read
    aws s3 cp cloudformation_templates/scheduler.yml s3://nops-rules-lambda-sources/scheduler/scheduler-uat.yml --acl public-read
    aws s3 cp cloudformation_templates/encrypted_ebs_kms_policy.yml s3://nops-rules-lambda-sources/scheduler/encrypted_ebs_kms_policy-uat.yml --acl public-read
fi


pip install --target ./essential_package -r src/nswitch_essential/requirements.txt
cp ./src/nswitch_essential/*.py ./essential_package
cd essential_package/
zip -r ../essential-latest.zip .
cd ..

if [ "$ENV" == "prod" ];then
    aws s3 cp essential-latest.zip s3://nops-rules-lambda-sources/essential/essential-latest.zip --acl public-read
    aws s3 cp cloudformation_templates/essential.yml s3://nops-rules-lambda-sources/essential/essential.yml --acl public-read
else
    aws s3 cp essential-latest.zip s3://nops-rules-lambda-sources/essential/essential-latest-uat.zip --acl public-read
    aws s3 cp cloudformation_templates/essential.yml s3://nops-rules-lambda-sources/essential/essential-uat.yml --acl public-read
fi
