FROM python:3.7.7-buster

COPY . /app
WORKDIR /app

RUN pip install --default-timeout=1000 --no-cache-dir -r requirements.txt 
EXPOSE 5003 
ENTRYPOINT [ "python" ] 
CMD [ "main.py" ] 