FROM python
COPY . /Backend
RUN bash Backend/scripts/boot.sh
RUN pip3 install -r Backend/requirements.txt
WORKDIR /Backend
CMD flask run &
