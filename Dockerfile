#haproxy-view 

FROM python:3
MAINTAINER Bradley Cicenas <bradley.cicenas@gmail.com>

COPY requirements.txt /
RUN pip install -r requirements.txt

COPY . /app/
WORKDIR /app

ENTRYPOINT [ "python", "haproxyview.py" ] 
