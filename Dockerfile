FROM python:3-alpine

RUN mkdir -p /opt/gustos/kia_imgs/
COPY requirements.txt /opt/gustos/
RUN pip install -r /opt/gustos/requirements.txt
COPY stream.py config.json kia_images.json /opt/gustos/
ADD kia_imgs/ /opt/gustos/kia_imgs/
CMD ["python","/opt/gustos/stream.py"]

