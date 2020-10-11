FROM python:3-alpine

#RUN apk --no
WORKDIR /srv/hermes

COPY . /srv/hermes

RUN pip3 install -r requirements.txt \
    && adduser -D -h /home/hermes -s /bin/sh hermes

USER hermes

RUN mkdir /home/hermes/.hermes

CMD ["run_hermes", "-vv"]
