FROM python
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && DEBIAN_FRONTEND="noninteractive" TZ="America/Bogota" apt-get install -y tzdata
RUN apt-get install -y git python3-venv python3-pip python3-dev systemd build-essential libssl-dev libffi-dev python3-setuptools nginx awscli ffmpeg && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean
USER root
EXPOSE 8080 8080
