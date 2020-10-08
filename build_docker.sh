#!/bin/bash

# Get Login Session from AWS ECR & Execute
docker build --rm=true -t gustos .
docker tag gustos:latest 146563464137.dkr.ecr.us-east-1.amazonaws.com/gustos:latest
output=$(aws ecr get-login --no-include-email --region us-east-1 ) && $output
docker push 146563464137.dkr.ecr.us-east-1.amazonaws.com/gustos:latest
#cp config.json ~/Dropbox/stuff/creds/gustos/config.json
echo "the docker build is complete"
