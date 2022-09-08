# General-purpose Operating System for Augmented Interfaces

Base repository of the GOSAI project. This is an open-source and collaborative project to create augmented reality plateforms.

![placeholder](docs/gosai_banner.png)

## Requirements

Docker is required to use this project

Edit the .env file to to set your dockerhub username, the repository you want to push it to, the name of the platform you are using and optional device and version to keep track of changes.

## Quickstart

|Action                 |Command      |
|:----------------------|:------------|
|Build the image        |`make build` |
|Launch (with docker)   |`make launch`|
|Stop                   |`make stop`  |
|Push on Docker         |`make push`  |
|Pull from Docker       |`make pull`  |

## Deployement

The following method uses `systemctl` to ready GOSAI for demos.

Create a service in `/home/{USER}/.config/systemd/user/` called `gosai.service`. This service needs to use `make launch` in the project repository. See the example `./build/gosai.service`.

## Install an exisisting project

To install an existing project, simply clone the project in a directory called home. For example, use `git clone https://github.com/GOSAI-DVIC/second-self.git home` inside the gosai repository project to install the second-self project.

## Create your own project

Refer to [this tutorial](https://dvic.devinci.fr/tutorial/how-to-program-on-GOSAI) to learn how to develop on gosai.

## Developping

### Boot in a virtual environment : 

`python3 -m venv .venv `
`pip3 install -r build/cpu/requirements.txt`
`source .venv/bin/activate && make boot`