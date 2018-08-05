FROM ubuntu:18.04

# Install some essentials
RUN apt-get update
RUN apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common \
    build-essential

# Install docker
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
RUN add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
RUN apt-get update
RUN apt-get install -y docker-ce

# Install gcloud and kubectl
RUN curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-210.0.0-linux-x86_64.tar.gz
RUN tar -xvf google-cloud-sdk-210.0.0-linux-x86_64.tar.gz
RUN rm google-cloud-sdk-210.0.0-linux-x86_64.tar.gz
RUN bash google-cloud-sdk/install.sh -q --additional-components kubectl
ENV PATH="/google-cloud-sdk/bin:${PATH}"

WORKDIR /app

COPY . .

ENTRYPOINT [ "/bin/bash", "docker-entrypoint.sh" ]

CMD [ "test" ]