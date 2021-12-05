FROM python
COPY . /Backend
RUN pip3 install -r Backend/requirements.txt
RUN bash Backend/scripts/boot.sh
WORKDIR /Backend
CMD flask run &
