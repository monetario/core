NAME = monetario/api

.PHONY: all build tag_latest push build_dev tag_dev push_dev

all: build tag_latest push

build:
	docker build -t $(NAME):latest --no-cache .

build_dev:
	docker build -t $(NAME):dev --no-cache -f Dockerfile-dev .

tag_dev:
	docker tag -f $(NAME):dev docker.io/$(NAME):dev

tag_latest:
	docker tag -f $(NAME):latest docker.io/$(NAME):latest

push:
	docker push docker.io/$(NAME):latest

push_dev:
	docker push docker.io/$(NAME):dev
