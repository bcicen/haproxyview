# haproxyview
Simple web interface for aggregating and displaying HAproxy servers and stats.

# Overview

# Quickstart

Create a config.yml file using sample_config.yml for reference and mount it inside a Docker container: 

```
docker pull bcicen/haproxy-view:latest
docker run -d -p 8000:8000 -v /path/to/config.yml:/app/haproxyview/config.yml haproxy-view:latest
```
