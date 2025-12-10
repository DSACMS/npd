FROM amd64/ubuntu:22.04
RUN apt-get update && apt-get install -y curl sudo jq buildah

# RUN curl -o runner.tar.gz -L https://github.com/actions/runner/releases/download/v2.329.0/actions-runner-linux-x64-2.329.0.tar.gz
COPY runner.tar.gz .

RUN newuser=runner && \
    adduser --disabled-password --gecos "" $newuser && \
    usermod -aG sudo $newuser && \
    echo "$newuser ALL=(ALL) NOPASSWD:ALL" >/etc/sudoers

USER runner
WORKDIR /home/runner

RUN sudo mv /runner.tar.gz ./runner.tar.gz && \
    sudo chown runner:runner ./runner.tar.gz && \
    mkdir runner && \
    tar xzf runner.tar.gz -C runner && \
    rm runner.tar.gz
WORKDIR /home/runner/runner

RUN sudo ./bin/installdependencies.sh
# Alias buildah to docker to support building docker images without docker
RUN printf '#!/bin/bash\nbuildah "$@"\n' | sudo tee /usr/bin/docker > /dev/null && \
    sudo chmod +x /usr/bin/docker

COPY start.sh start.sh
ENTRYPOINT ["./start.sh"]