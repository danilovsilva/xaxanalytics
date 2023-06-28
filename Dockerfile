FROM public.ecr.aws/lambda/python:3.9

LABEL version="1.0"
LABEL maintainer="danilovsilva@outlook.com"

# Environment variable to set as PRD or DEV
ENV ENV PRD

# install common software
RUN yum install -y software-properties-common wget tar vim gzip

# Install GoLang 1.20.5
RUN wget -O /tmp/go.tgz https://go.dev/dl/go1.20.5.linux-amd64.tar.gz
RUN tar -C /usr/local -xzf /tmp/go.tgz
RUN rm /tmp/go.tgz
ENV PATH="$PATH:/usr/local/go/bin"

# Copy project files
COPY . ${LAMBDA_TASK_ROOT}

# Install Python dependencies
RUN pip3 install -r ${LAMBDA_TASK_ROOT}/requirements.txt

# Expose port
EXPOSE 80

# Exec command
CMD [ "main.handler" ]
