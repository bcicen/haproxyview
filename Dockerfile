#haproxy-view 

FROM python:2
MAINTAINER Bradley Cicenas <bradley.cicenas@gmail.com>

COPY requirements.txt /
RUN pip install -r requirements.txt

COPY . /app/

CMD /bin/bash /app/run.sh
