FROM python:3-alpine
MAINTAINER "Angel Rivera"

RUN mkdir -p /opt/gustos
COPY stream.py config.json requirements.txt /opt/gustos/
RUN pip install -r /opt/gustos/requirements.txt
CMD ["python","/opt/gustos/stream.py"]

