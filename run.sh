#!/bin/bash

# Build image
docker build \
  --build-arg USER=$USER \
  --build-arg UID=$(id -u $USER) \
  --build-arg GID=$(id -g $USER) \
  -t olimex/test1 .

# Run new instance
docker run -i -t \
	--privileged \
	-v /tmp:/tmp \
	-v /dev:/dev \
	-v /proc:/proc \
	-v $(pwd):/home/$USER/olimage \
  -v /etc/group:/etc/group:ro \
  -v /etc/passwd:/etc/passwd:ro \
  -v /etc/shadow:/etc/shadow:ro \
  -u $(id -u $USER):$(id -g $USER) \
	-w /home/$USER/olimage \
	olimex/test1

