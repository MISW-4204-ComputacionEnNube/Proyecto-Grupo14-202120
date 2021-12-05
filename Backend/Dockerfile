FROM python
COPY requirements.txt /
RUN pip3 install -r /requirements.txt
COPY . /Backend
WORKDIR /Backend
CMD flask run -p ${PORT} -h 0.0.0.0
