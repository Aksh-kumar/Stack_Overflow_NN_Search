FROM python:3.7.7-buster
ENV http_proxy http://10.10.5.18:8080/ 
ENV https_proxy http://10.10.5.18:8080/ 
COPY . /app
WORKDIR /app
RUN pip install --no-cache-dir pip==20.0.2
RUN pip install --no-cache-dir cython
RUN pip install --no-cache-dir pkgconfig
RUN pip install --no-cache-dir numpy==1.17.1
RUN pip install --no-cache-dir pandas==0.25.1
RUN pip install --no-cache-dir matplotlib==3.1.1
RUN pip install --default-timeout=1000 --no-cache-dir -r requirements.txt 
EXPOSE 5001 
ENTRYPOINT [ "python" ] 
CMD [ "main.py" ] 