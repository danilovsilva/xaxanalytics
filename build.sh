#!/bin/bash

# Cleaning
# aws lambda delete-function --function-name xaxanalytics
# sleep 5
# aws ecr delete-repository --repository-name xaxanalytics --force



# Creating
docker build -t xaxanalytics .
sleep 5
cd "/mnt/c/projects/xaxanalytics_parser"
sleep 5
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 561462040985.dkr.ecr.us-east-2.amazonaws.com
sleep 5
aws ecr create-repository --repository-name xaxanalytics --image-scanning-configuration scanOnPush=true --image-tag-mutability MUTABLE
sleep 5
docker tag xaxanalytics:latest 561462040985.dkr.ecr.us-east-2.amazonaws.com/xaxanalytics:latest
sleep 5
docker push 561462040985.dkr.ecr.us-east-2.amazonaws.com/xaxanalytics:latest
sleep 5
