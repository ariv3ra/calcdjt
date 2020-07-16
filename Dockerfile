FROM python:3-alpine

RUN mkdir -p /opt/gustos
COPY stream.py config.json kia_images.json requirements.txt /opt/gustos/
COPY kia_imgs/ /opt/gustos/
RUN pip install -r /opt/gustos/requirements.txt
CMD ["python","/opt/gustos/stream.py"]

