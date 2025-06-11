#!/bin/bash

skaffold deploy -p test \
                --images=app-image="europe-west4-docker.pkg.dev/gcp-automated-blog-test/autoblog-test-gar/blog-ai-assistant-be:56ae683",aws-image="europe-west4-docker.pkg.dev/gcp-automated-blog-test/autoblog-test-gar/blog-ai-assistant-aws-tunnel:fef2779"