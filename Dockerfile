# Docker Image for kdb

FROM prologic/crux-python
MAINTAINER James Mills <prologic@shortcircuitnet.au>

# Install dependencies
RUN prt-get depinst enchant

# Install Source
RUN pip install hg+https://bitbucket.org/prologic/kdb#egg=kdb

# Expose Service
EXPOSE 8000

# Startup
ENTRYPOINT ["/usr/bin/kdb"]
