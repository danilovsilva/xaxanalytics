# xaxanalytics Readme file

## Building the docker container

To build the docker file you will need to install the AWS CLI
https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

> Linux
>>      curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
>>      unzip awscliv2.zip
>>      sudo ./aws/install

## Process to build the docker image

First you need to build the image
>> docker build -t xaxanalytics .

After this you need to start your container
If you need to start in a interactive mode run:
>> # docker run -it --name xaxanalytics xaxanalytics bash

If you need to start as a service to hear any port run:
>> docker run -p 9000:8080 --name xaxanalytics xaxanalytics
Then you can test this using a cUrl command:
>> curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'


## The process on AWS to build your environment is:
Get the AWS ECR login and pipe it to docker login command (remember to change the region and "561462040985" account id):
>> aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 561462040985.dkr.ecr.us-east-2.amazonaws.com

Create a ECR repositoty:
>> aws ecr create-repository --repository-name xaxanalytics --image-scanning-configuration scanOnPush=true --image-tag-mutability MUTABLE

Tag your container and send this information to your repository
>> docker tag xaxanalytics:latest 561462040985.dkr.ecr.us-east-2.amazonaws.com/xaxanalytics:latest

Push your image to AWS ECR container
>> docker push 561462040985.dkr.ecr.us-east-2.amazonaws.com/xaxanalytics:latest

Now you should create the lambda function:
>> aws lambda create-function \
>>   --function-name hello-world \
>>   --package-type Image \
>>   --code ImageUri=111122223333.dkr.ecr.us-east-1.amazonaws.com/hello-world:latest \
>>   --role arn:aws:iam::111122223333:role/lambda-ex
