FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl unzip \
    && rm -rf /var/lib/apt/lists/*

# Add V2Ray
ADD https://github.com/v2fly/v2ray-core/releases/latest/download/v2ray-linux-64.zip /tmp/v2ray.zip
RUN unzip /tmp/v2ray.zip -d /usr/local/bin/ \
    && rm /tmp/v2ray.zip \
    && chmod +x /usr/local/bin/v2ray 

# Copy your V2Ray config
COPY config.json /etc/v2ray/config.json

EXPOSE 1080 1081

ENTRYPOINT ["v2ray", "-config", "/etc/v2ray/config.json"]
