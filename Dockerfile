FROM python:3.5-slim

RUN apt-get update && apt-get install -y libatlas3-base libblas3 libc6 libgfortran3 liblapack3 libgcc1 libjpeg62 libpq5

RUN pip install --upgrade pip && mkdir -p /app

# Non privelaged user
RUN adduser --disabled-password --gecos '' --no-create-home webapp && chown -R webapp:webapp /app

WORKDIR /app
ENV HOME /app
ENV PATH /env/bin:$PATH

COPY requirements.txt $HOME/
RUN pip install -r requirements.txt
COPY . $HOME/
