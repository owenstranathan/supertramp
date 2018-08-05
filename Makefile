SHELL:=/bin/bash
NAME=$(shell basename $(shell pwd))
IMAGE=appfigures/$(NAME):$(shell git rev-parse HEAD)
BRANCH=$(shell git rev-parse --abbrev-ref HEAD)

ifeq ("$(BRANCH)", "master")
	ENVIRONMENT=production
endif

ifeq ("$(BRANCH)", "develop")
	ENVIRONMENT=staging
endif

ifeq ("$(CI)", "true")
	TRAVIS_IMAGE="$(TRAVIS_REPO_SLUG):$(TRAVIS_BUILD_NUMBER)"
	ifeq ("$(TRAVIS_BRANCH)", "master")
		MASTER=1
	endif
endif

.PHONY: all build push inspect clean generate-k8s

name:
	@echo $(NAME)

image:
	@echo $(IMAGE)

build: Dockerfile
	docker build . -t $(IMAGE) --build-arg PYPI_USERNAME=$(PYPI_USERNAME) --build-arg PYPI_PASSWORD=$(PYPI_PASSWORD)	
	if [[ "$(MASTER)" ]]; then docker tag $(IMAGE) $(LATEST); fi;

inspect:
	docker inspect --type=image $(IMAGE)

push: inspect
	if [[ "$(shell docker info | grep Username)" == "" ]]; then docker login -u="$(DOCKER_USERNAME)" -p="$(DOCKER_PASSWORD)"; fi
	docker push $(IMAGE)
	if [[ "$(CI)" ]]; then docker tag $(IMAGE) $(TRAVIS_IMAGE); docker push $(TRAVIS_IMAGE); echo "pushed $(TRAVIS_IMAGE)"; fi;
	if [[ "$(MASTER)" ]]; then docker push $(LATEST); echo "pushed $(LATEST)"; fi;

run:
	docker run -it --env-file ./.env -p 3000:3000 -v /var/run/docker.sock:/var/run/docker.sock $(IMAGE)

generate-k8s:
	@NAME=$(NAME) ENVIRONMENT=$(ENVIRONMENT) IMAGE=$(IMAGE) templater k8s-template.yaml > k8s.yaml

deploy: generate-k8s
	@kubectl get -f k8s.yaml > /dev/null || kubectl create -f k8s.yaml
	@if [ "$$?" == "0" ]; then \
		kubectl patch -f k8s.yaml -p '{"spec": {"image": "$(IMAGE)"}}';\
	fi

redeploy: generate-k8s
	kubectl replace -f k8s.yaml

undeploy: generate-k8s
	kubectl delete -f k8s.yaml

status: generate-k8s
	@kubectl get -f k8s.yaml -o wide