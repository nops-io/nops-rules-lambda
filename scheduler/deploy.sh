#!/bin/bash
ENV="$1"

mkdir ./scheduler_package
cp ./src/nswitch_scheduler/*.py ./scheduler_package
cd scheduler_package/
zip -r ../main-latest.zip .
cd ..

if [ "$ENV" == "prod" ];then
    aws s3 cp main-latest.zip s3://nops-rules-lambda-sources/scheduler/main-latest.zip --acl public-read
    aws s3 cp cloudformation_templates/scheduler-stackset.yml s3://nops-rules-lambda-sources/scheduler/scheduler-stackset.yml --acl public-read
    aws s3 cp cloudformation_templates/encrypted_ebs_kms_policy.yml s3://nops-rules-lambda-sources/essentials/encrypted_ebs_kms_policy.yml --acl public-read
else
    aws s3 cp main-latest.zip s3://nops-rules-lambda-sources/scheduler/main-latest-uat.zip --acl public-read
    aws s3 cp cloudformation_templates/scheduler-stackset.yml s3://nops-rules-lambda-sources/scheduler/scheduler-stackset-uat.yml --acl public-read
    aws s3 cp cloudformation_templates/encrypted_ebs_kms_policy.yml s3://nops-rules-lambda-sources/essentials/encrypted_ebs_kms_policy-uat.yml --acl public-read
fi


mkdir ./essential_package
cp ./src/nswitch_essential/*.py ./essential_package
cd essential_package/
zip -r ../essential-latest.zip .
cd ..

if [ "$ENV" == "prod" ];then
    aws s3 cp essential-latest.zip s3://nops-rules-lambda-sources/essential/essential-latest.zip --acl public-read
    aws s3 cp cloudformation_templates/essential-stackset.yml s3://nops-rules-lambda-sources/essential/essential-stackset.yml --acl public-read
else
    aws s3 cp essential-latest.zip s3://nops-rules-lambda-sources/essential/essential-latest-uat.zip --acl public-read
    aws s3 cp cloudformation_templates/essential-stackset.yml s3://nops-rules-lambda-sources/essential/essential-stackset-uat.yml --acl public-read
fi


mkdir ./essentials_package
cp ./src/essentials/*.py ./essentials_package
cd essentials_package/
zip -r ../essentials-latest.zip .
cd ..

aws s3 cp essentials-latest.zip s3://nops-rules-lambda-sources/essentials/essentials-lambda-codes-latest.zip --acl public-read
aws s3 cp cloudformation_templates/essentials.yaml s3://nops-rules-lambda-sources/essentials/essentials-latest.yaml --acl public-read

if [ "$ENV" == "prod" ];then
    aws s3 cp cloudformation_templates/essentials_encrypted_ebs_kms_policy_all.yml s3://nops-rules-lambda-sources/essentials/essentials_encrypted_ebs_kms_policy_all.yml --acl public-read
else
    aws s3 cp cloudformation_templates/essentials_encrypted_ebs_kms_policy_all.yml s3://nops-rules-lambda-sources/essentials/essentials_encrypted_ebs_kms_policy_all-uat.yml --acl public-read
fi
