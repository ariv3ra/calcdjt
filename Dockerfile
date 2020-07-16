FROM python:3-alpine

RUN mkdir -p /opt/gustos/kia_imgs/
COPY stream.py config.json kia_images.json requirements.txt /opt/gustos/
ADD kia_imgs/ /opt/gustos/kia_imgs/
RUN pip install -r /opt/gustos/requirements.txt
CMD ["python","/opt/gustos/stream.py"]

