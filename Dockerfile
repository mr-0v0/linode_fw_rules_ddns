FROM python:slim-bullseye

RUN apt-get update && apt-get -y install locales

# Set the locale
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN mkdir -p /app

ADD main.py /app
ADD retry.py /app
ADD requirements.txt /app

RUN pip install -r /app/requirements.txt

CMD ["python", "/app/main.py"]
