FROM amd64/ubuntu:22.04
RUN apt-get update && apt-get install -y curl sudo jq

ADD https://github.com/actions/runner/releases/download/v2.316.0/actions-runner-linux-x64-2.316.0.tar.gz runner.tar.gz

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

COPY start.sh start.sh
ENTRYPOINT ["./start.sh"]