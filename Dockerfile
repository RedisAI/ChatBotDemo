FROM python:3.7-stretch
RUN apt-get update -y
RUN pip install redisai numpy flask flask-cors ml2rt
WORKDIR /app
ENTRYPOINT [ "flask" ]
CMD [ "run", "-h", "0.0.0.0" ]