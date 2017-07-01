#!/bin/bash

# Get Login Session from AWS ECR & Execute
output=$(aws --profile datapunks ecr get-login --region us-east-1 ) && $output
docker build --rm=true -t gustos .
docker tag gustos:latest 146563464137.dkr.ecr.us-east-1.amazonaws.com/gustos:latest
docker push 146563464137.dkr.ecr.us-east-1.amazonaws.com/gustos:latest
echo "the docker build is complete"
