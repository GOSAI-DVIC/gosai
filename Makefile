SHELL := /bin/zsh

.PHONY: build

include home/.env

IMNAME = ${USER}/${REPO}
TAG = ${PLATFORM}-${DEVICE}-${VERSION}
REDIS_REPO = redis
REDIS_IMNAME = docker.io/bitnami/redis:7.0

boot:DeepfakeScript
	-docker rm $(REPO)-$(REDIS_REPO)
	docker run -d --network="host" -e ALLOW_EMPTY_PASSWORD=yes --name=$(REPO)-$(REDIS_REPO) $(REDIS_IMNAME)
	sleep 0.5
	python3 init.py 

DeepfakeScript:
	# conda activate first-order
	source ~/anaconda3/bin/activate first-order && python home/scripts/app.py &

install:
	pip3 install -r build/cpu/requirements.txt

build:
	docker build -t $(IMNAME):$(TAG) -f build/${DEVICE}/Dockerfile .

push:
	docker push $(IMNAME):$(TAG)

pull:
	docker pull $(IMNAME):$(TAG)

launch:
	-docker rm $(REPO)-$(REDIS_REPO)
	-sudo xhost +local:root
	docker run -d --network="host" -e ALLOW_EMPTY_PASSWORD=yes --name=$(REPO)-$(REDIS_REPO) $(REDIS_IMNAME)
	sleep 2
	-docker rm $(REPO)
ifeq (${DEVICE}, gpu)
	docker run --expose 8000 -e PYTHONUNBUFFERED=1 --network="host" --privileged --volume=/dev:/dev -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY -e QT_X11_NO_MITSHM=1 --name=$(REPO) $(IMNAME):$(TAG)
else
	docker run --expose 8000 --network="host" --privileged --volume=/dev:/dev -e DISPLAY -e QT_X11_NO_MITSHM=1 --name=$(REPO) $(IMNAME):$(TAG)
endif

stop:
	-pkill -9 -f "start-fullscreen --incognito --disable-logging http://127.0.0.1:8000/gosai"
	-pkill -9 -f "python3 init.py"
	-docker stop $(REPO)
	-docker stop $(REPO)-$(REDIS_REPO)


calibration:
	python3 core/calibration/calibration_auto.py

background:
	python3 core/calibration/capture_empty_bg.py
