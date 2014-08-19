# Docker Image for kdb

FROM prologic/crux-python
MAINTAINER James Mills <prologic@shortcircuitnet.au>

# Install dependencies
RUN prt-get depinst aspell-en enchant

# Add Source
ADD . /usr/src/kdb

# Build and Install
RUN cd /usr/src/kdb && python setup.py install
RUN cd /usr/src/kdb && cp -r etc /etc/kdb

# Expose Service
EXPOSE 8000

# Startup
ENTRYPOINT ["/usr/bin/kdb"]
