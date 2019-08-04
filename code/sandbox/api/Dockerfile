FROM python:3.6

WORKDIR /code/

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD triangle triangle
WORKDIR /code/triangle
RUN make

WORKDIR /code
ADD server server
