#!/bin/bash

# Build image
docker build -t olimex/test1 .

docker run -i -t \
	--privileged \
	-v /tmp:/tmp \
	-v /dev:/dev \
	-v /proc:/proc \
	-v $(pwd):/olimage \
	-w /olimage \
	olimex/test1
