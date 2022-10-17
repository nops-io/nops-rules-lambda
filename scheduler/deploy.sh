#!/bin/bash
pip install --target ./package -r src/requirements.txt
cp ./src/main.py ./package
cd package/
zip -r ../main-latest.zip .
cd ..
aws s3 cp main-latest.zip s3://nops-rules-lambda-sources/scheduler/main-latest.zip --acl public-read
aws s3 cp scheduler.yml s3://nops-rules-lambda-sources/scheduler/scheduler.yml --acl public-read