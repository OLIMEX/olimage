#!/bin/bash

# Build image
docker build . -t olimex/test1

# Run new instance
docker run -i -t \
	--privileged \
	-v /tmp:/tmp \
	-v /dev:/dev \
	-v $(pwd):/olimage \
	olimex/test1

