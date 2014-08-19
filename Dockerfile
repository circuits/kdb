# Docker Image for kdb

FROM prologic/crux-python
MAINTAINER James Mills <prologic@shortcircuitnet.au>

# Services
EXPOSE 8000

# Startup
ENTRYPOINT ["/usr/bin/kdb"]

# Runtime Dependencies
RUN prt-get depinst aspell-en enchant

# Runtime Dependencies
ADD requirements.txt /tmp/requirements.txt
RUN pip install --allow-all-external -r /tmp/requirements.txt && rm /tmp/requirements.txt

# Application
WORKDIR /app
ADD etc /etc/kdb
ADD . /app
RUN pip install -e .
