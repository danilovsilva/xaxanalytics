# FROM public.ecr.aws/lambda/python:3.9
FROM ubuntu:20.04

LABEL version="1.0"
LABEL maintainer="danilovsilva@outlook.com"

# Environment variable to set as PRD or DEV
ENV env PRD

# install common software
RUN apt-get update
RUN apt-get install -y software-properties-common wget tar vim gzip

# Install Python 3.9
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get install -y python3.9 python3-pip
RUN rm -rf /usr/bin/python3
RUN ln -s /usr/bin/python3.9 /usr/bin/python3

# Install GoLang 1.20.5
RUN wget -O /tmp/go.tgz https://go.dev/dl/go1.20.5.linux-amd64.tar.gz
RUN tar -C /usr/local -xzf /tmp/go.tgz
RUN rm /tmp/go.tgz
ENV PATH="$PATH:/usr/local/go/bin"

ENV GOPATH /tmp/go
RUN go env -w GOMODCACHE=/tmp/go/pkg/mod
ENV GOCACHE /tmp/.cache/go-build
RUN mkdir -p /tmp/go /tmp/.cache/go-build



# Copy project files
RUN mkdir /app
WORKDIR /app
COPY . /app/

# Install Python dependencies
RUN pip3 install -r /app/requirements.txt

# Expose port
EXPOSE 80

# Exec command
CMD ["go", "version"]
CMD ["python3", "/app/main.py", "handler"]




# docker build -t xaxanalytics .

# docker run -it --name xaxanalytics xaxanalytics bash
# docker run -p 9000:8080 --name xaxanalytics xaxanalytics
# curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'



# aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 561462040985.dkr.ecr.us-east-2.amazonaws.com
# aws ecr create-repository --repository-name xaxanalytics --image-scanning-configuration scanOnPush=true --image-tag-mutability MUTABLE
# docker tag xaxanalytics:latest 561462040985.dkr.ecr.us-east-2.amazonaws.com/xaxanalytics:latest
# docker push 561462040985.dkr.ecr.us-east-2.amazonaws.com/xaxanalytics:latest
