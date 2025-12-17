#!/bin/bash
# Run this on your EC2 instance to update services

echo "Logging into ECR..."
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 058421552617.dkr.ecr.us-east-1.amazonaws.com

echo "Pulling latest images..."
docker-compose -f docker-compose.prod.yml pull

echo "Restarting services with new images..."
docker-compose -f docker-compose.prod.yml up -d

echo "Pruning old images..."
docker image prune -f

echo "Deployment Complete!"