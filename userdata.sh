#!/bin/bash

REGION=us-east-1
INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
SPOT_REQ_ID=$(aws --region $REGION ec2 describe-instances --instance-ids "$INSTANCE_ID"  --query 'Reservations[0].Instances[0].SpotInstanceRequestId' --output text)
if [ "$SPOT_REQ_ID" != "None" ] ; then
  TAGS=$(aws --region $REGION ec2 describe-spot-instance-requests --spot-instance-request-ids "$SPOT_REQ_ID" --query 'SpotInstanceRequests[0].Tags')
  aws --region $REGION ec2 create-tags --resources "$INSTANCE_ID" --tags "$TAGS"
fi

sudo yum -y update
sudo yum install -y ecs-init
sudo touch /etc/ecs/ecs.config
sudo echo 'ECS_CLUSTER=casablanca' > /etc/ecs/ecs.config
sudo echo 'ECS_AVAILABLE_LOGGING_DRIVERS=["json-file","syslog","awslogs","fluentd"]' >> /etc/ecs/ecs.config


sudo service docker start
sudo start ecs