FROM python:2-alpine
MAINTAINER "Angel Rivera" <ariv3ra@gmail.com>

RUN mkdir -p /opt/djt
COPY stream.py config.json requirements.txt /opt/djt/
RUN pip install -r /opt/djt/requirements.txt
CMD ["python","/opt/djt/stream.py"]

