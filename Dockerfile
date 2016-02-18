#haproxy-view 

FROM python:3

COPY requirements.txt /
RUN pip install -r requirements.txt

COPY . /app/
WORKDIR /app

ENTRYPOINT [ "python", "haproxyview.py" ] 
