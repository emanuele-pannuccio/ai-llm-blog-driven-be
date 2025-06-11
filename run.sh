#!/bin/bash

skaffold deploy -p test \
                --images=app-image="europe-west4-docker.pkg.dev/gcp-automated-blog-test/autoblog-test-gar/blog-ai-assistant-be:7861f9b",aws-image="europe-west4-docker.pkg.dev/gcp-automated-blog-test/autoblog-test-gar/blog-ai-assistant-aws-tunnel:fef2779"