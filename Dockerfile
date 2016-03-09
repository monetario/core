FROM python:3.5
MAINTAINER Sergey Nuzhdin <ipaq.lw@gmail.com>

RUN mkdir -p '/opt/monetario/core'
VOLUME ['/opt/monetario/core']

WORKDIR /opt/monetario/core

ADD ./requirements.txt /opt/requirements-core.txt

RUN pip install -r /opt/requirements-core.txt

EXPOSE 9000
