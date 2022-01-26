.PHONY: build

include platform/.env

IMNAME = ${USER}/${REPO}
TAG = ${PLATFORM}-${DEVICE}-${VERSION}
REDIS_REPO = redis
REDIS_IMNAME = docker.io/bitnami/redis:6.2

boot:
	python3 init.py

install:
	pip3 install -r build/cpu/requirements.txt

build:
	docker build -t $(IMNAME):$(TAG) -f build/${DEVICE}/Dockerfile .

push:
	docker push $(IMNAME):$(TAG)

pull:
	docker pull $(IMNAME):$(TAG)

launch:
	-sudo xhost +local:root
	-docker rm $(REPO)-$(REDIS_REPO)
	docker run -d --network="host" -e ALLOW_EMPTY_PASSWORD=yes --name=$(REPO)-$(REDIS_REPO) $(REDIS_IMNAME)
	sleep 2
ifeq (${DEVICE}, gpu)
	-docker rm $(REPO)
	docker run --expose 5000 -e PYTHONUNBUFFERED=1 --network="host" --privileged --volume=/dev:/dev -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY -e QT_X11_NO_MITSHM=1 --name=$(REPO) $(IMNAME):$(TAG)
else
	-docker rm $(REPO)
	docker run -d --expose 5000 --network="host" --privileged --volume=/dev:/dev -e DISPLAY -e QT_X11_NO_MITSHM=1 --name=$(REPO) $(IMNAME):$(TAG)
endif

stop:
	-docker stop $(REPO)
	-docker stop $(REPO)-$(REDIS_REPO)
