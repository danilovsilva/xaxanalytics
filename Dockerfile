FROM ubuntu:20.04

LABEL version="1.0"
LABEL maintainer="seu_email@example.com"

# Environment variable to set as PRD or DEV
ENV ENV PRD

# Update repositories and install common software
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y software-properties-common wget tar vim

# Install Python 3.9
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get install -y python3.9 python3-pip
RUN rm -rf /usr/bin/python3
RUN ln -s /usr/bin/python3.9 /usr/bin/python3

# Install GoLang 1.20.5
RUN wget -O go.tgz https://go.dev/dl/go1.20.5.linux-amd64.tar.gz
RUN tar -C /usr/local -xzf go.tgz
RUN rm go.tgz
ENV PATH="$PATH:/usr/local/go/bin"

# Create project directories
RUN mkdir /app
WORKDIR /app

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip3 install -r /app/requirements.txt

# Expose port
EXPOSE 80

# Run the main.py script
CMD ["/main.sh"]

# docker build -t xaxanalytics .
# docker run -it --name xaxanalytics xaxanalytics bash
